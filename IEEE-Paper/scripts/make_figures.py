"""Generate the paper's data figures from mock_data.json (real results; the file name is historical).

Usage (from IEEE-Paper/):  python scripts/make_figures.py
Requires: matplotlib.  Output: figures/*.pdf (vector, for LaTeX) + figures/*.png (preview).

Every block whose "is_mock" is true is stamped with a diagonal "MOCK DATA" watermark,
so a placeholder figure can never be mistaken for a real result.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
DATA = json.loads((Path(__file__).parent / "mock_data.json").read_text(encoding="utf-8"))

# Categorical slots in fixed order (validated reference palette), text in neutral ink.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
COL_W = 3.45  # IEEE single-column width (inches)


def watermark(fig, is_mock: bool) -> None:
    if is_mock:
        fig.text(0.5, 0.5, "MOCK DATA", fontsize=26, color="#d03b3b", alpha=0.18, ha="center", va="center",
                 rotation=25, weight="bold", zorder=100)


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=220)
    plt.close(fig)
    print("wrote", name)


def grouped_bars(ax, groups: list[str], series: dict[str, list[float]], ylim=(0, 1.0), fmt="{:.2f}") -> None:
    n = len(series)
    width = 0.8 / n
    x = np.arange(len(groups))
    for i, (name, vals) in enumerate(series.items()):
        pos = x - 0.4 + width * (i + 0.5)
        bars = ax.bar(pos, vals, width * 0.92, color=SERIES[i], label=name, zorder=3, linewidth=0)
        if i == 0:  # selective direct labels: only the proposed system
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01 * (ylim[1] - ylim[0]), fmt.format(v),
                        ha="center", va="bottom", fontsize=6, color=INK)
    ax.set_xticks(x, groups)
    ax.set_ylim(*ylim)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def fig_cnn_comparison() -> None:
    d = DATA["cnn_comparison"]
    fig, ax = plt.subplots(figsize=(COL_W, 2.1))
    grouped_bars(ax, d["metrics"], d["systems"], ylim=(0.90, 1.0), fmt="{:.3f}")
    ax.set_ylabel("Score (out-of-fold, 5-fold CV)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=1, frameon=False)
    watermark(fig, d["is_mock"])
    save(fig, "fig_cnn_comparison")


def fig_confusion() -> None:
    d = DATA["cnn_confusion"]
    m = np.array(d["matrix"], dtype=float)
    norm = m / m.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(COL_W * 0.82, 2.5))
    im = ax.imshow(norm, cmap="Blues", vmin=0, vmax=1)
    for i in range(len(m)):
        for j in range(len(m)):
            ax.text(j, i, f"{norm[i, j]:.2f}", ha="center", va="center", fontsize=6.5,
                    color="white" if norm[i, j] > 0.55 else INK)
    ax.set_xticks(range(len(m)), d["classes"], rotation=30, ha="right")
    ax.set_yticks(range(len(m)), d["classes"])
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("True class")
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.ax.tick_params(labelsize=6)
    cb.outline.set_visible(False)
    watermark(fig, d["is_mock"])
    save(fig, "fig_confusion")


def fig_rag_ablation() -> None:
    d = DATA["rag_ablation"]
    fig, ax = plt.subplots(figsize=(COL_W, 2.2))
    labels = [c.replace(" (", "\n(").replace(" + ", "\n+ ") for c in d["configs"]]
    grouped_bars(ax, labels, {"Recall@3": d["Recall@3"], "nDCG@3": d["nDCG@3"]}, ylim=(0.3, 1.0))
    ax.set_ylabel("Retrieval score")
    ax.tick_params(axis="x", labelsize=6)
    ax.legend(loc="upper left", ncol=2, frameon=False)
    watermark(fig, d["is_mock"])
    save(fig, "fig_rag_ablation")


def fig_generation() -> None:
    d = DATA["generation_comparison"]
    fig, ax = plt.subplots(figsize=(COL_W, 2.1))
    systems = {k: [np.nan if v is None else v for v in vals] for k, vals in d["systems"].items()}
    grouped_bars(ax, d["metrics"], systems, ylim=(0, 1.05))
    ax.set_ylabel("Mean score")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=1, frameon=False)
    watermark(fig, d["is_mock"])
    save(fig, "fig_generation")


def fig_latency() -> None:
    d = DATA["measured_latency"]
    fig, ax = plt.subplots(figsize=(COL_W, 1.7))
    y = np.arange(len(d["stages"]))[::-1]
    ax.barh(y, d["seconds"], height=0.55, color=SERIES[0], zorder=3, linewidth=0)
    for yi, v in zip(y, d["seconds"]):
        label = (f"{v * 1000:.1f} ms" if v < 0.1 else f"{v * 1000:.0f} ms") if v < 1 else f"≈{v:.0f} s"
        ax.text(v * 1.15, yi, label, va="center", fontsize=6.5, color=INK)
    ax.set_yticks(y, d["stages"])
    ax.set_xscale("log")
    ax.set_xlim(0.002, 40)
    ax.set_xlabel("Latency (seconds, log scale)")
    ax.xaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    watermark(fig, d["is_mock"])
    save(fig, "fig_latency")


if __name__ == "__main__":
    fig_cnn_comparison()
    fig_confusion()
    fig_rag_ablation()
    fig_generation()
    fig_latency()
