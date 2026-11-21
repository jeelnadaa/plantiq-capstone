"""Run one TrainConfig over all folds: train, predict val + test, save predictions, resume if interrupted."""
from __future__ import annotations

import gc
import json

import torch

from . import config, data, env
from .metrics import classification_metrics
from .train import TrainConfig, fit, measure_cost, predict, save_preds


def preds_path(model: str, fold: int, split: str):
    return config.CNN_PREDS / f"{model}_fold{fold}_{split}.csv"


def folds_to_run(only=None):
    n = 1 if config.SMOKE else config.N_FOLDS
    return list(range(n)) if only is None else list(only)


def run_cv(cfg: TrainConfig, device, uniq, splits, images, folds=None, skip_existing=True) -> dict:
    labels = uniq["label"].to_numpy()
    eval_tf = data.build_transform("eval", cfg.size)
    train_tf = data.build_transform(cfg.train_aug, cfg.size)
    per_fold, last_model = {}, None
    for k in folds_to_run(folds):
        hist_file = config.RUNS_DIR / cfg.name / f"fold{k}" / "history.json"
        if skip_existing and hist_file.exists() and preds_path(cfg.name, k, "test").exists():
            info = json.loads(hist_file.read_text())
            print(f"[{cfg.name}] fold {k}: already done (delete {hist_file.parent} to retrain), skipping")
            per_fold[k] = {"best_epoch": info["best_epoch"], "train_minutes": info["train_minutes"],
                           "test": info.get("test_metrics")}
            continue
        idx = data.fold_indices(uniq, splits, k)
        print(f"\n=== {cfg.name} | fold {k} | train {len(idx['train'])} val {len(idx['val'])} "
              f"test {len(idx['test'])} byte-unique images ===")
        tl = data.make_loader(images, uniq, idx["train"], train_tf, batch_size=cfg.batch_size, train=True,
                              sampler_mode=cfg.sampler, samples_per_epoch=cfg.samples_per_epoch,
                              workers=cfg.workers, seed=config.SEED + k)
        vl = data.make_loader(images, uniq, idx["val"], eval_tf, batch_size=128, train=False, workers=0)
        te = data.make_loader(images, uniq, idx["test"], eval_tf, batch_size=128, train=False, workers=0)
        res = fit(cfg, tl, vl, device, config.RUNS_DIR / cfg.name / f"fold{k}")
        model = res["model"]
        for split, loader in (("val", vl), ("test", te)):
            lg, y, j = predict(model, loader, device)
            save_preds(preds_path(cfg.name, k, split), uniq, lg, y, j)
            if split == "test":
                tm = classification_metrics(y, lg.argmax(1))
        print(f"[{cfg.name}] fold {k} TEST acc {tm['accuracy']:.4f} macro-F1 {tm['macro_f1']:.4f}")
        info = json.loads(hist_file.read_text())
        info["test_metrics"] = tm
        hist_file.write_text(json.dumps(info, indent=2))
        per_fold[k] = {"best_epoch": res["best_epoch"], "train_minutes": res["train_minutes"], "test": tm}
        last_model = model.cpu()
        del tl, vl, te, res
        gc.collect()
        torch.cuda.empty_cache()
    summary = {"model": cfg.name, "config": cfg.to_dict(), "folds": per_fold, "meta": env.run_meta()}
    env.write_json(config.CNN_RESULTS / f"{cfg.name}_summary.json", summary)
    if last_model is None:  # every fold was skipped: rebuild the last fold's model for the cost measurement
        from .train import build_model

        k = folds_to_run(folds)[-1]
        last_model = build_model(cfg.arch, pretrained=False)
        last_model.load_state_dict(torch.load(config.RUNS_DIR / cfg.name / f"fold{k}" / "best.pt",
                                              map_location="cpu", weights_only=True))
    torch.cuda.empty_cache()
    cost = measure_cost(last_model, cfg.size, cfg.name)
    env.write_json(config.CNN_RESULTS / f"{cfg.name}_cost.json", cost)
    print("cost:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in cost.items()})
    return summary
