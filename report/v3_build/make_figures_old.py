"""Figures for the patched report with the ORIGINAL report data (run from report/v3_build/)."""
import matplotlib.pyplot as plt
from make_figures import box, arrow, canvas, save, INK, HEAD, BODY, EDGE, ACC, ACCE, EXT


def fig_architecture():
    W, H = 10.0, 5.3
    fig, ax = canvas(W, H)
    cols = [
        ("1. Client and inputs", ["Mobile APK / web PWA\n(Capacitor 7)", "Estate GPS\ncoordinates",
                                  "Leaf photo upload", "Voice or text query\n(Kannada / English)",
                                  "Crop lot details\nand photos"]),
        ("2. Perception and\nprocessing", ["Microclimate service\n(Open-Meteo,\nspore-risk score)",
                                          "Module 1\nResNet-50 classifier", "Speech-to-text chain\n+ language pre-router",
                                          "Module 4\nmarketplace"]),
        ("3. AI reasoning\nand advisory", ["Module 2\nhybrid RAG", "LLM advisory\n(Gemini, Groq failover)",
                                          "Module 3\nmultimodal chatbot"]),
        ("4. Storage and\noutcomes", ["FAISS knowledge base", "Relational database\n(users, cache, chats,\nlistings)",
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
    save(fig, "old_fig5_1_architecture.png")


def fig_rag():
    W, H = 9.0, 9.4
    fig, ax = canvas(W, H)
    cx, bw, bh = 4.3, 5.2, 0.56
    rows = [
        ("Diagnosis (class, confidence) + question", BODY, EDGE),
        ("Query expanded with the disease name", BODY, EDGE),
        None,
        ("Stage 2: reciprocal rank fusion (k = 60)", BODY, EDGE),
        ("Filter to passages tagged with the diagnosed disease", BODY, EDGE),
        ("Stage 3: MiniLM cross-encoder rerank, sigmoid score: top 3", BODY, EDGE),
        ("Prompt: disease + weather + 3 passages + question", "#dde8f4", HEAD),
        ("Gemini 2.5 Flash, then Groq, then retrieved CCRI text", BODY, EDGE),
        ("Dosage audit against the retrieved passages", BODY, EDGE),
        ("Advice + Verified / Caution label", "#dde8f4", HEAD),
    ]
    y = H - 0.25
    centres = []
    for r in rows:
        if r is None:
            sw = 2.45
            box(ax, cx - sw - 0.15, y - 0.78, sw, 0.78, "Stage 1a: dense search\nBGE-base-en + FAISS, top 15")
            box(ax, cx + 0.15, y - 0.78, sw, 0.78, "Stage 1b: sparse search\nBM25, top 15")
            centres.append(("split", y, y - 0.78))
            y -= 0.78 + 0.32
            continue
        text, fc, ec = r
        box(ax, cx - bw / 2, y - bh, bw, bh, text, fc=fc, ec=ec, fs=10.5)
        centres.append(("one", y, y - bh))
        y -= bh + 0.32
    for (k1, t1, b1), (k2, t2, b2) in zip(centres, centres[1:]):
        if k2 == "split":
            arrow(ax, cx, b1, cx - 1.37, t2)
            arrow(ax, cx, b1, cx + 1.37, t2)
        elif k1 == "split":
            arrow(ax, cx - 1.37, b1, cx, t2)
            arrow(ax, cx + 1.37, b1, cx, t2)
        else:
            arrow(ax, cx, b1, cx, t2)
    _, t, b = centres[2]
    box(ax, 0.05, b - 1.25, 1.55, 0.95, "Offline index\nof CCRI\npassages", fc=EXT, ec="#888", dashed=True, fs=10)
    arrow(ax, 0.82, b - 0.30, cx - 1.9, b + 0.05, dashed=True, color="#555")
    _, t, b = centres[6]
    box(ax, cx + bw / 2 + 0.3, b - 0.18, 1.5, 0.92, "Open-Meteo\nweather,\nfavourability", fc=ACC, ec=ACCE, fs=10)
    arrow(ax, cx + bw / 2 + 0.3, b + 0.28, cx + bw / 2, b + 0.28)
    save(fig, "old_fig6_1_rag_pipeline.png")


def fig_speech():
    W, H = 9.6, 6.6
    fig, ax = canvas(W, H)
    lx, bw, bh = 0.2, 3.6, 0.62
    chain = ["Voice input recorded in the app", "Resample to 16 kHz",
             "Tier 1 (local): IndicConformer-600M (Kannada)\nor Svarah Whisper (English)",
             "Failover 1 (cloud): Groq whisper-large-v3", "Failover 2 (cloud): Gemini Audio"]
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
        ax.text(lx + bw / 2 + 0.08, ys[i][0] + 0.15, "if the tier fails", fontsize=9, color="#555", style="italic")
    tx = 5.1
    box(ax, tx, ys[2][1], 4.2, ys[2][0] - ys[2][1], "Transcribed text", fc="#dde8f4", ec=HEAD, fs=10.5)
    for i in (2, 3, 4):
        mid = (ys[i][0] + ys[i][1]) / 2
        arrow(ax, lx + bw, mid, tx, (ys[2][0] + ys[2][1]) / 2, dashed=(i != 2), color=INK if i == 2 else "#555")
    r = [("Pre-router: Unicode check for Kannada\nscript (regular expression, 0.08 ms)", BODY, EDGE),
         ("Kannada: English search query +\ninstruction to reply in Kannada script", BODY, EDGE),
         ("Hybrid retrieval and language model", "#dde8f4", HEAD)]
    y = ys[2][1] - 0.35
    prev = ys[2][1]
    for t, fc, ec in r:
        box(ax, tx, y - 0.78, 4.2, 0.78, t, fc=fc, ec=ec, fs=10)
        arrow(ax, tx + 2.1, prev, tx + 2.1, y)
        prev = y - 0.78
        y -= 0.78 + 0.35
    ax.text(lx + bw / 2, ys[-1][1] - 0.35, "Speech-to-text chain", ha="center", va="top",
            fontsize=11.5, fontweight="bold", color=INK)
    ax.text(tx + 2.1, ys[2][0] + 0.35, "Language pre-router", ha="center", va="bottom",
            fontsize=11.5, fontweight="bold", color=INK)
    save(fig, "old_fig6_2_speech_chain.png")


def fig_accuracy():
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    labels = ["Validation set", "New leaves"]
    vals = [90.0, 80.0]
    bars = ax.bar(labels, vals, color=["#2f5d8a", "#a9bdd3"], width=0.5, edgecolor=INK, linewidth=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v:.0f}%", ha="center", fontsize=11)
    ax.axhline(75, color="#b03a2e", ls="--", lw=1.1, label="75% confidence gate")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False, fontsize=10)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Accuracy (%)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "old_fig8_1_accuracy.png")


def fig_latency():
    ops = [("Script detection (pre-router)", 0.08), ("CNN cache hit", 0.85),
           ("CNN warm inference", 14.2), ("CNN cold start", 704)]
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    names = [o[0] for o in ops][::-1]
    vals = [o[1] for o in ops][::-1]
    bars = ax.barh(names, vals, color="#2f5d8a", edgecolor=INK, linewidth=0.5, height=0.55)
    ax.set_xscale("log")
    ax.set_xlim(0.03, 8000)
    for b, v in zip(bars, vals):
        ax.text(v * 1.18, b.get_y() + b.get_height() / 2, f"{v:g} ms", va="center", fontsize=10)
    ax.set_xlabel("Time (ms, logarithmic scale)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save(fig, "old_fig8_2_latency.png")


if __name__ == "__main__":
    fig_architecture()
    fig_rag()
    fig_speech()
    fig_accuracy()
    fig_latency()
    print("old figures written")
