"""Model builders, one training loop for every PyTorch model, prediction and cost (latency/params/FLOPs)."""
from __future__ import annotations

import copy
import io
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from . import config
from .metrics import classification_metrics

N_CLS = len(config.CLASSES)


# --------------------------------------------------------------------------- models
def build_model(arch: str, pretrained: bool = True) -> nn.Module:
    from torchvision import models

    if arch in ("resnet50_linear", "resnet50_dropout"):
        m = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2 if pretrained else None)
        m.fc = (nn.Linear(m.fc.in_features, N_CLS) if arch == "resnet50_linear"
                else nn.Sequential(nn.Dropout(0.4), nn.Linear(m.fc.in_features, N_CLS)))  # backend head
        return m
    if arch == "googlenet":
        # Anudeep K.S. et al.: GoogLeNet transfer learning, fine-tuning the last three layers. In torchvision the
        # last three layers are inception5a, inception5b and fc; everything before them is frozen.
        if pretrained:  # ImageNet weights include the auxiliary heads; drop them after loading
            m = models.googlenet(weights=models.GoogLeNet_Weights.IMAGENET1K_V1)
            m.aux_logits, m.aux1, m.aux2 = False, None, None
        else:
            m = models.googlenet(weights=None, aux_logits=False, init_weights=True)
        m.fc = nn.Linear(m.fc.in_features, N_CLS)
        for name, p in m.named_parameters():
            p.requires_grad = name.startswith(("inception5a", "inception5b", "fc"))
        return m
    raise ValueError(arch)


def load_deployed() -> nn.Module:
    """The weights currently shipped in backend/data/models, rebuilt exactly as backend/app/services/cnn.py does."""
    m = build_model("resnet50_dropout", pretrained=False)
    state = torch.load(str(config.DEPLOYED_WEIGHTS), map_location="cpu", weights_only=True)
    m.load_state_dict(state)
    return m


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


# --------------------------------------------------------------------------- config
@dataclass
class TrainConfig:
    name: str
    arch: str = "resnet50_dropout"
    size: int = 224
    train_aug: str = "leaf"              # plain | autoaugment | leaf
    sampler: str = "balanced"            # copies | balanced
    samples_per_epoch: int | None = 6000  # None = one pass over the published files (copies) / unique images
    epochs: int = 25
    batch_size: int = 64
    optimizer: str = "adamw"             # adamw | adam
    lr: float = 1e-3
    weight_decay: float = 0.01
    backbone_lr_mult: float = 1.0        # <1: smaller LR for pretrained layers than for the new head
    scheduler: str = "cosine_warmup"     # cosine_epoch (original notebook) | cosine_warmup | constant
    warmup_epochs: float = 1.0
    label_smoothing: float = 0.0
    ema_decay: float | None = None
    mixup: bool = False
    select: str = "val_macro_f1"         # val_acc | val_macro_f1 | last (checkpoint selection on validation only)
    tie_break_loss: bool = True          # equal val score -> keep the epoch with lower val loss (val saturates at 1.0)
    patience: int | None = None
    workers: int = 3                     # 3 loader processes: keeps up with the GPU, ~1.5 GB RAM each on Windows
    notes: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def _param_groups(model, cfg: TrainConfig):
    head = [p for n, p in model.named_parameters() if p.requires_grad and n.startswith("fc")]
    body = [p for n, p in model.named_parameters() if p.requires_grad and not n.startswith("fc")]
    groups = [{"params": head, "lr": cfg.lr}]
    if body:
        groups.append({"params": body, "lr": cfg.lr * cfg.backbone_lr_mult})
    return groups


def _optimizer(model, cfg: TrainConfig):
    groups = _param_groups(model, cfg)
    if cfg.optimizer == "adamw":
        return torch.optim.AdamW(groups, lr=cfg.lr, weight_decay=cfg.weight_decay)
    if cfg.optimizer == "adam":
        return torch.optim.Adam(groups, lr=cfg.lr, weight_decay=cfg.weight_decay)
    raise ValueError(cfg.optimizer)


def _scheduler(opt, cfg: TrainConfig, steps_per_epoch: int):
    if cfg.scheduler == "cosine_epoch":   # stepped once per epoch, T_max = epochs (original notebook)
        return torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=cfg.epochs), "epoch"
    if cfg.scheduler == "constant":
        return None, None
    total = cfg.epochs * steps_per_epoch
    warm = max(1, int(cfg.warmup_epochs * steps_per_epoch))

    def f(step):
        if step < warm:
            return (step + 1) / warm
        return 0.5 * (1 + math.cos(math.pi * min(1.0, (step - warm) / max(1, total - warm))))

    return torch.optim.lr_scheduler.LambdaLR(opt, f), "step"


# --------------------------------------------------------------------------- predict
@torch.no_grad()
def predict(model, loader, device) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    model.eval()
    logits, labels, idx = [], [], []
    for x, y, j in loader:
        x = x.to(device, non_blocking=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"):
            out = model(x)
        logits.append(out.float().cpu())
        labels.append(y)
        idx.append(j)
    return torch.cat(logits).numpy(), torch.cat(labels).numpy(), torch.cat(idx).numpy()


def save_preds(path: Path, uniq: pd.DataFrame, logits: np.ndarray, labels: np.ndarray, idx: np.ndarray) -> None:
    df = pd.DataFrame({"path": uniq["path"].to_numpy()[idx], "group_id": uniq["group_id"].to_numpy()[idx],
                       "y_true": labels})
    for c in range(logits.shape[1]):
        df[f"logit_{c}"] = logits[:, c]
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


# --------------------------------------------------------------------------- train
def fit(cfg: TrainConfig, train_loader, val_loader, device, run_dir: Path, log_every: int = 1) -> dict:
    """Train one model. The checkpoint with the best validation score (cfg.select) is kept and returned."""
    from torch.optim.swa_utils import AveragedModel, get_ema_multi_avg_fn
    from torchvision.transforms import v2 as T

    run_dir.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(config.SEED)
    model = build_model(cfg.arch).to(device)
    opt = _optimizer(model, cfg)
    sched, sched_unit = _scheduler(opt, cfg, len(train_loader))
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    crit = nn.CrossEntropyLoss(label_smoothing=cfg.label_smoothing)
    ema = AveragedModel(model, multi_avg_fn=get_ema_multi_avg_fn(cfg.ema_decay), use_buffers=True) \
        if cfg.ema_decay else None
    mix = T.RandomChoice([T.MixUp(alpha=0.2, num_classes=N_CLS), T.CutMix(alpha=1.0, num_classes=N_CLS)]) \
        if cfg.mixup else None

    epochs = 1 if config.SMOKE else cfg.epochs
    history, best, best_loss, best_state, best_epoch, bad = [], -1.0, float("inf"), None, 0, 0
    t_start = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        t0, seen, loss_sum, correct = time.time(), 0, 0.0, 0
        for x, y, _ in train_loader:
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)
            target = y
            if mix is not None and torch.rand(1).item() < 0.5:
                x, target = mix(x, y)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"):
                out = model(x)
                loss = crit(out, target)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            if ema is not None:
                ema.update_parameters(model)
            if sched_unit == "step":
                sched.step()
            seen += x.size(0)
            loss_sum += loss.item() * x.size(0)
            correct += (out.argmax(1) == y).sum().item()
        if sched_unit == "epoch":
            sched.step()
        eval_model = ema.module if ema is not None else model
        v_logits, v_y, _ = predict(eval_model, val_loader, device)
        vm = classification_metrics(v_y, v_logits.argmax(1))
        v_loss = nn.functional.cross_entropy(torch.from_numpy(v_logits), torch.from_numpy(v_y)).item()
        rec = {"epoch": epoch, "train_loss": loss_sum / max(1, seen), "train_acc": correct / max(1, seen),
               "val_loss": v_loss, "val_acc": vm["accuracy"], "val_macro_f1": vm["macro_f1"],
               "img_per_s": seen / (time.time() - t0), "lr": opt.param_groups[0]["lr"]}
        history.append(rec)
        score = float(epoch) if cfg.select == "last" else rec[cfg.select]   # 'last' = keep the final epoch
        improved = score > best or (cfg.tie_break_loss and cfg.select != "last" and score == best and v_loss < best_loss)
        if improved:
            best, best_loss, best_epoch, bad = score, v_loss, epoch, 0
            best_state = copy.deepcopy(eval_model.state_dict())
        else:
            bad += 1
        if epoch % log_every == 0 or improved:
            print(f"[{cfg.name}] ep {epoch:02d}/{epochs} loss {rec['train_loss']:.4f} acc {rec['train_acc']:.3f} | "
                  f"val loss {v_loss:.4f} acc {vm['accuracy']:.3f} mF1 {vm['macro_f1']:.3f} "
                  f"| {rec['img_per_s']:.0f} img/s{'  *' if improved else ''}")
        if cfg.patience and bad >= cfg.patience:
            print(f"[{cfg.name}] early stop at epoch {epoch} (best {best_epoch})")
            break
    minutes = (time.time() - t_start) / 60
    final = ema.module if ema is not None else model
    final.load_state_dict(best_state)
    torch.save(final.state_dict(), run_dir / "best.pt")
    info = {"config": cfg.to_dict(), "history": history, "best_epoch": best_epoch, "best_val": best,
            "best_val_loss": best_loss,
            "train_minutes": minutes, "epochs_run": len(history)}
    (run_dir / "history.json").write_text(json.dumps(info, indent=2))
    print(f"[{cfg.name}] done in {minutes:.1f} min, best {cfg.select}={best:.4f} at epoch {best_epoch}")
    return {"model": final, **info}


# --------------------------------------------------------------------------- cost
def measure_cost(model: nn.Module, size: int, name: str, gpu: bool = True) -> dict:
    """Params, file size, GFLOPs and batch-1 latency (median / p95 ms) on GPU and CPU."""
    from torch.utils.flop_counter import FlopCounterMode

    model = copy.deepcopy(model).float().eval().cpu()
    n_warm, n_runs = (2, 5) if config.SMOKE else (20, 200)
    buf = io.BytesIO()
    torch.save(model.state_dict(), buf)
    x = torch.randn(1, 3, size, size)
    with torch.no_grad(), FlopCounterMode(display=False) as fc:
        model(x)
    out = {"model": name, "input_size": size, "params": count_params(model), "size_mb": buf.tell() / 1e6,
           "gflops": fc.get_total_flops() / 1e9, "cpu_threads": torch.get_num_threads()}

    def timed(m, xin, sync):
        with torch.inference_mode():
            for _ in range(n_warm):
                m(xin)
            ts = []
            for _ in range(n_runs):
                sync()
                t = time.perf_counter()
                m(xin)
                sync()
                ts.append((time.perf_counter() - t) * 1000)
        return float(np.median(ts)), float(np.percentile(ts, 95))

    out["cpu_ms_median"], out["cpu_ms_p95"] = timed(model, x, lambda: None)
    if gpu and torch.cuda.is_available():
        mg = model.cuda()
        out["gpu_ms_median"], out["gpu_ms_p95"] = timed(mg, x.cuda(), torch.cuda.synchronize)
        model.cpu()
    return out
