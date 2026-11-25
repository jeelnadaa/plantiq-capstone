"""Redraws the five report figures as crisp 300-dpi PNGs (run from report/v3_build/)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})
DPI = 300
INK = "#1f2a36"
HEAD = "#2f5d8a"
BODY = "#eef3f9"
EDGE = "#6b88a8"
ACC = "#e8f3e6"
ACCE = "#5f8f57"
EXT = "#f4f4f4"


def box(ax, x, y, w, h, text, fc=BODY, ec=EDGE, tc=INK, bold=False, fs=10.5, dashed=False):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.06",
                       fc=fc, ec=ec, lw=1.1, ls="--" if dashed else "-")
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc,
            fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, dashed=False, color=INK):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13,
                                 lw=1.2, color=color, ls="--" if dashed else "-",
                                 shrinkA=0, shrinkB=0))


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(name, dpi=DPI, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Figure 5.1
def fig_architecture():
    W, H = 10.0, 5.75
    fig, ax = canvas(W, H)
    cols = [
        ("1. Client and inputs", ["Mobile APK / web app\n(Capacitor 7)", "Estate GPS\ncoordinates",
                                  "Leaf photo upload", "Voice or text query\n(Kannada / English)",
                                  "Crop lot details\nand photos"]),
        ("2. Perception and\nprocessing", ["Microclimate service\n(Open-Meteo, risk level,\nspray window)",
                                          "Module 1\nResNet-50 classifier", "Speech-to-text chain\n+ language router",
                                          "Module 4\nmarketplace"]),
        ("3. AI reasoning\nand advisory", ["Module 2\nhybrid RAG", "LLM advisory\n(Gemini, Groq,\noffline guide)",
                                          "Module 3\nmultimodal chatbot"]),
        ("4. Storage and\noutcomes", ["FAISS knowledge base\n(931 passages)",
                                     "Relational database\n(users, cache, chats,\nlistings)", "Media store\n(sanitised photos)",
                                     "Bilingual reply", "Maps / call /\nWhatsApp hand-off"]),
    ]
    cw, gap, x0 = 2.1, 0.38, 0.1
    top = H - 0.15
    for i, (title, items) in enumerate(cols):
        x = x0 + i * (cw + gap)
        box(ax, x, top - 0.78, cw, 0.78, title, fc=HEAD, ec=HEAD, tc="white", bold=True, fs=11.5)
        y = top - 0.78 - 0.22
        for it in items:
            h = 0.62 if it.count("\n") < 2 else 0.82
            box(ax, x + 0.08, y - h, cw - 0.16, h, it, fs=10)
            y -= h + 0.16
        if i < 3:
            arrow(ax, x + cw + 0.04, top - 0.39, x + cw + gap - 0.04, top - 0.39)
    save(fig, "fig5_1_architecture.png")


# ---------------------------------------------------------------- Figure 6.1
def fig_rag():
    W, H = 9.0, 9.4
    fig, ax = canvas(W, H)
    cx, bw, bh = 4.3, 5.2, 0.56
    rows = [
        ("Diagnosis (class, confidence) + question + language", BODY, EDGE),
        ("Language routing and query expansion with the disease name", BODY, EDGE),
        None,  # dense / sparse
        ("Stage 2: reciprocal rank fusion (k = 60)", BODY, EDGE),
        ("Stage 3: cross-encoder rerank, sigmoid score", BODY, EDGE),
        ("Topic preference (+0.1) and near-duplicate removal: top 3", BODY, EDGE),
        ("Prompt: disease + weather + 3 passages + question", "#dde8f4", HEAD),
        ("Gemini 2.5 Flash, then Groq, then offline guide", BODY, EDGE),
        ("Dosage audit against the retrieved passages", BODY, EDGE),
        ("Advice + sources + risk level + Verified / Caution", "#dde8f4", HEAD),
    ]
    y = H - 0.25
    centres = []
    for r in rows:
        if r is None:
            sw = 2.15
            box(ax, cx - sw - 0.15, y - 0.78, sw, 0.78, "Stage 1a: dense search\nbge-m3 + FAISS, top 20")
            box(ax, cx + 0.15, y - 0.78, sw, 0.78, "Stage 1b: sparse search\nBM25, top 20")
            centres.append(("split", y, y - 0.78))
            y -= 0.78 + 0.32
            continue
        text, fc, ec = r
        box(ax, cx - bw / 2, y - bh, bw, bh, text, fc=fc, ec=ec, fs=10.5)
        centres.append(("one", y, y - bh))
        y -= bh + 0.32
    for (k1, t1, b1), (k2, t2, b2) in zip(centres, centres[1:]):
        if k2 == "split":
            arrow(ax, cx, b1, cx - 1.22, t2)
            arrow(ax, cx, b1, cx + 1.22, t2)
        elif k1 == "split":
            arrow(ax, cx - 1.22, b1, cx, t2)
            arrow(ax, cx + 1.22, b1, cx, t2)
        else:
            arrow(ax, cx, b1, cx, t2)
    # offline index and weather side boxes
    _, t, b = centres[2]
    box(ax, 0.05, b - 1.25, 1.55, 0.95, "Offline index\n14 PDFs,\n931 passages", fc=EXT, ec="#888", dashed=True, fs=10)
    arrow(ax, 0.82, b - 0.30, cx - 1.9, b + 0.05, dashed=True, color="#555")
    _, t, b = centres[6]
    box(ax, cx + bw / 2 + 0.3, b - 0.18, 1.5, 0.92, "Open-Meteo\nweather, risk,\nspray window", fc=ACC, ec=ACCE, fs=10)
    arrow(ax, cx + bw / 2 + 0.3, b + 0.28, cx + bw / 2, b + 0.28)
    save(fig, "fig6_1_rag_pipeline.png")


# ---------------------------------------------------------------- Figure 6.2
def fig_speech():
    W, H = 9.6, 7.0
    fig, ax = canvas(W, H)
    # left column: speech chain
    lx, bw, bh = 0.2, 3.6, 0.62
    chain = ["Voice note recorded in the app\n(language chosen by the grower)",
             "Resample to 16 kHz mono",
             "Tier 1 (local): IndicConformer-600M (Kannada)\nor Svarah Whisper (English)",
             "Failover 1 (cloud): Groq whisper-large-v3",
             "Failover 2 (cloud): Gemini Audio"]
    ys = []
    y = H - 0.2
    for i, c in enumerate(chain):
        h = 0.78 if "\n" in c else bh
        box(ax, lx, y - h, bw, h, c, fc=ACC if i == 2 else BODY, ec=ACCE if i == 2 else EDGE, fs=10)
        ys.append((y, y - h))
        y -= h + 0.3
    for (t1, b1), (t2, b2) in zip(ys, ys[1:]):
        arrow(ax, lx + bw / 2, b1, lx + bw / 2, t2)
    for i in (3, 4):
        ax.text(lx + bw / 2 + 0.08, ys[i][0] + 0.15, "on failure or empty text", fontsize=9, color="#555", style="italic")
    # transcript box
    tx = 5.1
    box(ax, tx, ys[2][1], 4.2, ys[2][0] - ys[2][1], "Transcript placed in the input box\n(grower can correct it before sending)",
        fc="#dde8f4", ec=HEAD, fs=10)
    for i in (2, 3, 4):
        mid = (ys[i][0] + ys[i][1]) / 2
        arrow(ax, lx + bw, mid, tx, (ys[2][0] + ys[2][1]) / 2, dashed=(i != 2), color=INK if i == 2 else "#555")
    # router column
    r = [("Language router: LLM in JSON mode\n(language, one English question, reply language)", BODY, EDGE),
         ("Fallback: Unicode check for Kannada\nscript (U+0C80 to U+0CFF), 0.08 ms", EXT, "#888"),
         ("English question to hybrid retrieval;\nreply written in Kannada script", "#dde8f4", HEAD)]
    y = ys[2][1] - 0.35
    prev = ys[2][1]
    for j, (t, fc, ec) in enumerate(r):
        box(ax, tx, y - 0.78, 4.2, 0.78, t, fc=fc, ec=ec, fs=10, dashed=(j == 1))
        arrow(ax, tx + 2.1, prev, tx + 2.1, y)
        prev = y - 0.78
        y -= 0.78 + 0.35
    ax.text(lx + bw / 2, ys[-1][1] - 0.35, "Speech-to-text chain", ha="center", va="top",
            fontsize=11.5, fontweight="bold", color=INK)
    ax.text(tx + 2.1, ys[2][0] + 0.35, "Language pre-router", ha="center", va="bottom",
            fontsize=11.5, fontweight="bold", color=INK)
    save(fig, "fig6_2_speech_chain.png")


# ---------------------------------------------------------------- Figure 8.1
def fig_accuracy():
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    labels = ["Validation set\n(Phase 3 check)", "New leaves\n(Phase 3 check)",
              "Leak-free 5-fold CV\naccuracy", "Leak-free 5-fold CV\nmacro-F1"]
    vals = [90.0, 80.0, 97.9, 97.0]
    cols = ["#6b88a8", "#a9bdd3", "#2f5d8a", "#5f8f57"]
    bars = ax.bar(labels, vals, color=cols, width=0.58, edgecolor=INK, linewidth=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v:.1f}%", ha="center", fontsize=11)
    ax.axhline(75, color="#b03a2e", ls="--", lw=1.1, label="75% confidence gate")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False, fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Score (%)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "fig8_1_accuracy.png")


# ---------------------------------------------------------------- Figure 8.2
def fig_latency():
    ops = [("Script detection (fallback router)", 0.08), ("CNN cache hit", 0.85),
           ("CNN inference, GPU (median)", 5.3), ("CNN inference, CPU (median)", 54.9),
           ("Chat turn without the LLM (median)", 220), ("Hybrid retrieval", 400),
           ("CNN cold start", 704), ("Complete advisory", 6000)]
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    names = [o[0] for o in ops][::-1]
    vals = [o[1] for o in ops][::-1]
    bars = ax.barh(names, vals, color="#2f5d8a", edgecolor=INK, linewidth=0.5, height=0.6)
    ax.set_xscale("log")
    ax.set_xlim(0.03, 40000)
    for b, v in zip(bars, vals):
        lab = f"{v:g} ms" if v < 1000 else f"{v / 1000:g} s"
        ax.text(v * 1.18, b.get_y() + b.get_height() / 2, lab, va="center", fontsize=10)
    ax.set_xlabel("Time (ms, logarithmic scale)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=0.25, which="major")
    ax.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "fig8_2_latency.png")


if __name__ == "__main__":
    fig_architecture()
    fig_rag()
    fig_speech()
    fig_accuracy()
    fig_latency()
    print("figures written")
