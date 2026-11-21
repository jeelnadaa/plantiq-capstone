"""Every number in the CNN comparison is computed here, the same way for every model."""
from __future__ import annotations

import numpy as np

from . import config

K = len(config.CLASSES)


def softmax(logits: np.ndarray, T: float = 1.0) -> np.ndarray:
    z = logits / T
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def classification_metrics(y: np.ndarray, pred: np.ndarray) -> dict:
    from sklearn.metrics import (accuracy_score, balanced_accuracy_score, f1_score, precision_score,
                                 recall_score)

    labels = list(range(K))
    per_f1 = f1_score(y, pred, labels=labels, average=None, zero_division=0)
    return {
        "n": int(len(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, labels=labels, average="macro", zero_division=0)),
        "macro_precision": float(precision_score(y, pred, labels=labels, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y, pred, labels=labels, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if len(set(y)) > 1 else float("nan"),
        "per_class_f1": {c: float(f) for c, f in zip(config.CLASSES, per_f1)},
    }


def confusion(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    from sklearn.metrics import confusion_matrix

    return confusion_matrix(y, pred, labels=list(range(K)))


def ece(probs: np.ndarray, y: np.ndarray, bins: int = 15) -> float:
    """Expected Calibration Error with equal-width confidence bins."""
    conf = probs.max(1)
    correct = (probs.argmax(1) == y).astype(float)
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            total += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return float(total)


def fit_temperature(val_logits: np.ndarray, val_y: np.ndarray) -> float:
    """Temperature scaling (Guo et al. 2017): one scalar T minimising validation NLL. Does not change argmax."""
    import torch

    lg = torch.as_tensor(val_logits, dtype=torch.float64)
    yy = torch.as_tensor(val_y, dtype=torch.long)
    log_t = torch.zeros(1, dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS([log_t], lr=0.1, max_iter=200)

    def closure():
        opt.zero_grad()
        loss = torch.nn.functional.cross_entropy(lg / log_t.exp(), yy)
        loss.backward()
        return loss

    opt.step(closure)
    return float(np.clip(log_t.exp().item(), 0.05, 20.0))


def gate_stats(probs: np.ndarray, y: np.ndarray, thr: float = config.CONF_GATE) -> dict:
    """PlantIQ's confidence gate: predictions below `thr` are flagged as uncertain instead of answered."""
    conf, pred = probs.max(1), probs.argmax(1)
    answered = conf >= thr
    wrong = pred != y
    return {
        "threshold": thr,
        "coverage": float(answered.mean()),
        "accuracy_answered": float((~wrong[answered]).mean()) if answered.any() else float("nan"),
        "errors_total": int(wrong.sum()),
        "errors_caught_by_gate": int((wrong & ~answered).sum()),
        "share_errors_caught": float((wrong & ~answered).sum() / wrong.sum()) if wrong.any() else float("nan"),
    }


# --------------------------------------------------------------------------- uncertainty
def _metric_fn(name: str):
    if name == "accuracy":
        return lambda y, p: float((y == p).mean())
    if name == "macro_f1":
        from sklearn.metrics import f1_score

        return lambda y, p: float(f1_score(y, p, labels=list(range(K)), average="macro", zero_division=0))
    raise ValueError(name)


def _group_index(groups: np.ndarray):
    uniq, inv = np.unique(groups, return_inverse=True)
    members = [np.where(inv == g)[0] for g in range(len(uniq))]
    return members


def group_bootstrap_ci(y, pred, groups, metric="macro_f1", n_boot=2000, seed=config.SEED, alpha=0.05) -> dict:
    """95% CI that resamples SOURCE GROUPS (not files), so near-duplicate images cannot fake precision."""
    rng = np.random.default_rng(seed)
    f = _metric_fn(metric)
    members = _group_index(groups)
    vals = []
    for _ in range(200 if config.SMOKE else n_boot):
        pick = rng.integers(0, len(members), len(members))
        ix = np.concatenate([members[g] for g in pick])
        vals.append(f(y[ix], pred[ix]))
    lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"point": f(y, pred), "lo": float(lo), "hi": float(hi)}


def paired_bootstrap_diff(y, pred_a, pred_b, groups, metric="macro_f1", n_boot=2000, seed=config.SEED) -> dict:
    """metric(A) - metric(B) on the same images, group bootstrap. 'significant' if the 95% CI excludes 0."""
    rng = np.random.default_rng(seed)
    f = _metric_fn(metric)
    members = _group_index(groups)
    diffs = []
    for _ in range(200 if config.SMOKE else n_boot):
        pick = rng.integers(0, len(members), len(members))
        ix = np.concatenate([members[g] for g in pick])
        diffs.append(f(y[ix], pred_a[ix]) - f(y[ix], pred_b[ix]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    point = f(y, pred_a) - f(y, pred_b)
    return {"diff": float(point), "lo": float(lo), "hi": float(hi), "significant": bool(lo > 0 or hi < 0),
            "p_value_two_sided": float(min(1.0, 2 * min(np.mean(np.array(diffs) <= 0), np.mean(np.array(diffs) >= 0))))}


def mcnemar(y, pred_a, pred_b) -> dict:
    """Exact McNemar test on discordant pairs (A right & B wrong vs A wrong & B right)."""
    from scipy.stats import binomtest

    a_ok, b_ok = pred_a == y, pred_b == y
    n01 = int((a_ok & ~b_ok).sum())
    n10 = int((~a_ok & b_ok).sum())
    p = binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return {"a_right_b_wrong": n01, "a_wrong_b_right": n10, "p_value": float(p)}
