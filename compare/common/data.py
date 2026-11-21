"""Images in RAM, fold splits, transforms, samplers and data loaders (identical for every model)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

from . import config

CACHE = config.ROOT / "_cache"


# --------------------------------------------------------------------------- tables
def load_unique() -> pd.DataFrame:
    p = config.AUDIT_DIR / "unique.csv"
    if not p.exists():
        raise FileNotFoundError("Run 01_dataset_audit/01_dataset_audit.ipynb first (unique.csv missing).")
    return pd.read_csv(p)


def load_files() -> pd.DataFrame:
    return pd.read_csv(config.AUDIT_DIR / "files.csv")


def load_splits() -> pd.DataFrame:
    return pd.read_csv(config.AUDIT_DIR / "splits.csv")


def fold_indices(uniq: pd.DataFrame, splits: pd.DataFrame, fold: int) -> dict[str, np.ndarray]:
    """Row indices into `uniq` for train / val / test of one fold."""
    pos = pd.Series(np.arange(len(uniq)), index=uniq["path"])
    f = splits[splits.fold == fold]
    out = {s: pos[f.loc[f.split == s, "path"]].to_numpy() for s in ("train", "val", "test")}
    if config.SMOKE:  # tiny but class-complete subsets
        rng = np.random.default_rng(0)
        lab = uniq["label"].to_numpy()
        for s, n in (("train", 40), ("val", 10), ("test", 10)):
            out[s] = np.concatenate([rng.permutation(out[s][lab[out[s]] == c])[:n] for c in range(len(config.CLASSES))])
    return out


# --------------------------------------------------------------------------- pixels
def load_images(uniq: pd.DataFrame) -> torch.Tensor:
    """All byte-unique images as one uint8 tensor (N,3,128,128), cached in compare/_cache/."""
    from PIL import Image

    CACHE.mkdir(exist_ok=True)
    key = CACHE / f"images_{config.STORE_SIZE}_{len(uniq)}.npy"
    if key.exists():
        arr = np.load(key)
        if arr.shape[0] == len(uniq):
            return torch.from_numpy(arr)
    s = config.STORE_SIZE
    arr = np.empty((len(uniq), 3, s, s), dtype=np.uint8)
    for i, p in enumerate(uniq["path"]):
        with Image.open(config.DATA_DIR / p) as im:
            im = im.convert("RGB")
            if im.size != (s, s):
                im = im.resize((s, s), Image.BILINEAR)
            arr[i] = np.asarray(im).transpose(2, 0, 1)
    np.save(key, arr)
    return torch.from_numpy(arr)


class Dihedral(torch.nn.Module):
    """Random rotation by a multiple of 90 degrees plus optional mirror (8 orientations; a leaf patch has no 'up')."""

    def forward(self, x):
        k = int(torch.randint(0, 4, (1,)))
        x = torch.rot90(x, k, dims=(-2, -1))
        if torch.rand(1) < 0.5:
            x = torch.flip(x, dims=(-1,))
        return x


def build_transform(kind: str, size: int):
    """kind: 'eval' | 'plain' | 'autoaugment' | 'leaf'. Input: uint8 CHW tensor at 128x128."""
    from torchvision.transforms import v2 as T

    norm = [T.ToDtype(torch.float32, scale=True), T.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD)]
    resize = T.Resize((size, size), antialias=True)
    if kind in ("eval", "plain"):
        return T.Compose([resize, *norm])
    # Augmentations run at the stored 128x128 and the result is resized to `size` last: the source pixels are
    # 128x128 anyway, and this keeps CPU data loading ahead of the GPU at 224x224.
    s = config.STORE_SIZE
    if kind == "autoaugment":  # the original notebook: Resize(128) -> AutoAugment(ImageNet)
        return T.Compose([T.Resize((s, s), antialias=True), T.AutoAugment(T.AutoAugmentPolicy.IMAGENET), resize, *norm])
    if kind == "leaf":
        return T.Compose([Dihedral(), T.RandomResizedCrop(s, scale=(0.6, 1.0), antialias=True),
                          T.ColorJitter(0.3, 0.3, 0.3), resize, *norm, T.RandomErasing(p=0.25)])
    raise ValueError(kind)


def _worker_init(_):
    torch.set_num_threads(1)   # each loader process uses one core; avoids workers fighting over CPU threads


class ImageSet(Dataset):
    def __init__(self, images: torch.Tensor, labels: np.ndarray, idx: np.ndarray, transform):
        self.images, self.labels, self.idx, self.transform = images, labels, np.asarray(idx), transform

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, i):
        j = int(self.idx[i])
        return self.transform(self.images[j]), int(self.labels[j]), j


# --------------------------------------------------------------------------- sampling
def sample_weights(uniq: pd.DataFrame, idx: np.ndarray, mode: str) -> np.ndarray:
    """'copies'   : each byte-unique image weighted by how many files it has in the published dataset, i.e. the
                    distribution the original notebook trained on (iterating over all 58k files).
       'balanced' : every class equally likely; within a class every source group equally likely."""
    sub = uniq.iloc[idx]
    if mode == "copies":
        return sub["n_copies"].to_numpy(dtype=np.float64)
    if mode == "balanced":
        g_size = sub.groupby("group_id")["path"].transform("count").to_numpy()
        n_groups = sub.groupby("label")["group_id"].transform("nunique").to_numpy()
        return 1.0 / (len(config.CLASSES) * n_groups * g_size)
    raise ValueError(mode)


def make_loader(images, uniq, idx, transform, *, batch_size, train, sampler_mode=None, samples_per_epoch=None,
                workers=4, seed=config.SEED):
    labels = uniq["label"].to_numpy()
    ds = ImageSet(images, labels, idx, transform)
    kw = dict(batch_size=batch_size, num_workers=workers, pin_memory=True, persistent_workers=workers > 0,
              worker_init_fn=_worker_init if workers > 0 else None)
    if not train:
        return DataLoader(ds, shuffle=False, **kw)
    w = sample_weights(uniq, idx, sampler_mode)
    if samples_per_epoch:
        n = int(samples_per_epoch)
    elif sampler_mode == "copies":
        n = int(w.sum())          # one pass over all published files of the training groups
    else:
        n = len(idx)
    if config.SMOKE:
        n = min(n, 4 * batch_size)
    gen = torch.Generator().manual_seed(seed)
    sampler = WeightedRandomSampler(torch.as_tensor(w, dtype=torch.double), num_samples=n, replacement=True,
                                    generator=gen)
    return DataLoader(ds, sampler=sampler, drop_last=True, **kw)
