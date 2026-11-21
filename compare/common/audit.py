"""Dataset audit: exact duplicates (MD5), rotation/flip-invariant near duplicates, source groups, folds."""
from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

IMG_EXT = {".jpg", ".jpeg", ".png"}
PIXEL_SIZE = 48          # images are compared at 48x48 grayscale
PIXEL_THRESHOLD = 6.0    # mean absolute difference (0-255) below which two patches count as the same source


# --------------------------------------------------------------------------- scanning
def list_files(data_dir: Path = config.DATA_DIR) -> pd.DataFrame:
    rows = []
    for folder in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        if folder.name not in config.FOLDER_TO_CLASS:
            raise ValueError(f"Unexpected class folder: {folder.name}")
        for f in sorted(folder.iterdir()):
            if f.is_file() and f.suffix.lower() in IMG_EXT:
                rows.append({"path": f.relative_to(data_dir).as_posix(), "folder": folder.name,
                             "cls": config.FOLDER_TO_CLASS[folder.name]})
    return pd.DataFrame(rows)


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def add_md5(df: pd.DataFrame, data_dir: Path = config.DATA_DIR, workers: int = 16) -> pd.DataFrame:
    with ThreadPoolExecutor(workers) as ex:
        df = df.assign(md5=list(ex.map(_md5, (data_dir / p for p in df["path"]))))
    return df


# --------------------------------------------------------------------------- per-image features
def _dihedral(a: np.ndarray) -> list[np.ndarray]:
    """The 8 rotations/flips of a 2-D array."""
    out = []
    for k in range(4):
        r = np.rot90(a, k)
        out += [r, np.fliplr(r)]
    return out


def image_features(path: Path) -> dict:
    import imagehash
    from PIL import Image

    with Image.open(path) as im:
        w, h = im.size
        g64 = im.convert("L").resize((64, 64), Image.BILINEAR)
        g48 = np.asarray(im.convert("L").resize((PIXEL_SIZE, PIXEL_SIZE), Image.BILINEAR), dtype=np.float32)
    a64 = np.asarray(g64)
    inv = min(str(imagehash.phash(Image.fromarray(np.ascontiguousarray(v)))) for v in _dihedral(a64))
    return {"w": w, "h": h, "phash_inv": inv, "pix": g48}


# --------------------------------------------------------------------------- grouping
class _UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, i):
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def pixel_min_mad(pix: np.ndarray, device: str = "cuda") -> np.ndarray:
    """(n,n) matrix: smallest mean-absolute pixel difference between image i (any rotation/flip) and image j."""
    import torch

    n = len(pix)
    dev = device if (device == "cuda" and torch.cuda.is_available()) else "cpu"
    base = torch.from_numpy(pix.reshape(n, -1)).to(dev)
    variants = torch.from_numpy(np.stack([np.stack([np.ascontiguousarray(v) for v in _dihedral(p)]) for p in pix])
                                .reshape(n * 8, -1)).to(dev)
    out = torch.empty((n, n), device=dev)
    step = 256  # rows of i per chunk (x8 variants) keeps memory small
    for s in range(0, n, step):
        e = min(n, s + step)
        d = torch.cdist(variants[s * 8:e * 8], base, p=1) / base.shape[1]   # (chunk*8, n)
        out[s:e] = d.view(e - s, 8, n).amin(1)
    return out.cpu().numpy()


def assign_groups(uniq: pd.DataFrame, pix: np.ndarray) -> tuple[np.ndarray, dict]:
    """Union-find over byte-unique images (same class only): same invariant pHash OR pixel MAD < threshold."""
    n = len(uniq)
    uf = _UF(n)
    stats = {"phash_merges": 0, "pixel_merges": 0}
    cls = uniq["cls"].to_numpy()
    for c in config.CLASSES:
        idx = np.where(cls == c)[0]
        # identical invariant pHash
        first: dict[str, int] = {}
        for i in idx:
            h = uniq["phash_inv"].iat[i]
            if h in first:
                if uf.find(i) != uf.find(first[h]):
                    stats["phash_merges"] += 1
                uf.union(i, first[h])
            else:
                first[h] = i
        # pixel check
        d = pixel_min_mad(pix[idx])
        np.fill_diagonal(d, np.inf)
        ii, jj = np.where(d < PIXEL_THRESHOLD)
        for a, b in zip(idx[ii], idx[jj]):
            if uf.find(a) != uf.find(b):
                stats["pixel_merges"] += 1
            uf.union(a, b)
    roots = np.array([uf.find(i) for i in range(n)])
    _, group_id = np.unique(roots, return_inverse=True)
    return group_id, stats


def cross_class_matches(uniq: pd.DataFrame, files: pd.DataFrame) -> dict:
    """Duplicates whose copies carry different labels (would mean label noise)."""
    md5_cls = files.groupby("md5")["cls"].nunique()
    ph_cls = uniq.groupby("phash_inv")["cls"].nunique()
    return {"md5_groups_with_2plus_labels": int((md5_cls > 1).sum()),
            "phash_groups_with_2plus_labels": int((ph_cls > 1).sum())}


# --------------------------------------------------------------------------- splits
def make_splits(uniq: pd.DataFrame, n_folds: int = config.N_FOLDS, val_parts: int = 6,
                seed: int = config.SEED) -> pd.DataFrame:
    """Long table (fold, path, split). Test = one StratifiedGroupKFold fold; validation = 1/val_parts of the
    remaining groups (again group-stratified). A source group is never on two sides."""
    from sklearn.model_selection import StratifiedGroupKFold

    y = uniq["label"].to_numpy()
    g = uniq["group_id"].to_numpy()
    outer = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    rows = []
    for k, (trval, test) in enumerate(outer.split(np.zeros(len(y)), y, g)):
        inner = StratifiedGroupKFold(n_splits=val_parts, shuffle=True, random_state=seed + k)
        tr_rel, va_rel = next(inner.split(np.zeros(len(trval)), y[trval], g[trval]))
        for split, ids in (("train", trval[tr_rel]), ("val", trval[va_rel]), ("test", test)):
            rows += [{"fold": k, "path": uniq["path"].iat[i], "split": split} for i in ids]
    return pd.DataFrame(rows)


def check_splits(uniq: pd.DataFrame, splits: pd.DataFrame) -> pd.DataFrame:
    """Raises if any group leaks across train/val/test or a fold lacks a class; returns a per-fold summary."""
    m = splits.merge(uniq[["path", "cls", "group_id"]], on="path", validate="many_to_one")
    summary = []
    for k, f in m.groupby("fold"):
        sides = f.groupby("group_id")["split"].nunique()
        if (sides > 1).any():
            raise AssertionError(f"fold {k}: {int((sides > 1).sum())} groups appear in more than one split")
        if len(f) != len(uniq) or f["path"].duplicated().any():
            raise AssertionError(f"fold {k}: every byte-unique image must appear exactly once")
        for split in ("train", "val", "test"):
            present = set(f.loc[f.split == split, "cls"])
            if present != set(config.CLASSES):
                raise AssertionError(f"fold {k} {split}: missing classes {set(config.CLASSES) - present}")
        row = {"fold": k}
        for split in ("train", "val", "test"):
            s = f[f.split == split]
            row[f"{split}_images"] = len(s)
            row[f"{split}_groups"] = s["group_id"].nunique()
            row[f"{split}_healthy_groups"] = s.loc[s.cls == "Healthy", "group_id"].nunique()
        summary.append(row)
    test_paths = m[m.split == "test"]["path"]
    if test_paths.duplicated().any() or len(test_paths) != len(uniq):
        raise AssertionError("each image must be in exactly one test fold")
    return pd.DataFrame(summary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
