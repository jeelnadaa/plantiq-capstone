// Rebuilds the PlantIQ Review #3 deck (from PlantIQ_Review3.pdf) as an editable .pptx with updated content.
// One component set for every slide, so fonts, sizes and colours are identical across old and new material.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");

const OUT = process.argv[2];
const A = (f) => path.join(__dirname, "assets", f);

// ------------------------------------------------------------------ design tokens (measured from the PDF)
const C = {
  dark: "12301F", green: "2E7D4F", orange: "E8871E", sage: "8DB596", bg: "F2F5F0", white: "FFFFFF",
  line: "D5DDD3", chip: "DDE9DF", chipLine: "BFD4C4", chipText: "2E5E44", text: "1A1F1B", muted: "5E6E63",
  algo: "CDE6D3", rowAlt: "F5F8F4", met: "DCEFE2", metText: "1D6B3E", exc: "FBE6C8", excText: "8A4B0A",
  pageNum: "8A968C", red: "C0392B", brown: "5B3A29",
};
// The deck's typeface is Satoshi (Fontshare); large display titles use Satoshi Light. QA_FONT swaps in an installed
// font of similar width for preview renders on machines without Satoshi.
const F = process.env.QA_FONT || "Satoshi";
const F_LIGHT = process.env.QA_FONT || "Satoshi Light";
const S = { label: 11, title: 26, cardHead: 15, body: 13, table: 11.5, stat: 24, caption: 11, chip: 11, algo: 11.5,
            banner: 16, footer: 9, page: 10 };
const W = 13.333;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "PlantIQ - Project Progress Review #3";
pres.author = "PlantIQ Team";
pres.company = "PES University";
pres.theme = { headFontFace: F, bodyFontFace: F };

const shadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 90, color: "000000", opacity: 0.1 });

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// ------------------------------------------------------------------ components
let pageNo = 0;
function base(sl, { label, title, subtitle, dark }) {
  pageNo += 1;
  sl.background = { color: dark ? C.dark : C.bg };
  sl.addText(label.toUpperCase(), { x: 0.6, y: 0.24, w: 9, h: 0.3, fontFace: F, fontSize: S.label, color: C.orange,
    charSpacing: 3, margin: 0, isTextBox: true });
  sl.addText(title, { x: 0.6, y: 0.58, w: 10.6, h: 0.6, fontFace: F, fontSize: S.title, color: dark ? C.white : C.dark,
    margin: 0, isTextBox: true });
  if (subtitle) sl.addText(subtitle, { x: 0.6, y: 1.16, w: 11, h: 0.32, fontFace: F, fontSize: S.body, italic: true,
    color: C.muted, margin: 0, isTextBox: true });
  sl.addImage({ path: A("pes_logo.png"), x: 11.53, y: 0.28, w: 1.2, h: 0.615 });
  sl.addText("PlantIQ  ·  UE23CS441A Project Phase 3  ·  Review #3", { x: 0.6, y: 7.05, w: 6, h: 0.28,
    fontFace: F, fontSize: S.footer, color: C.muted, margin: 0, isTextBox: true });
  sl.addText(String(pageNo), { x: 12.13, y: 7.03, w: 0.6, h: 0.3, fontFace: F, fontSize: S.page, color: C.pageNum,
    align: "right", margin: 0, isTextBox: true });
}

function card(sl, x, y, w, h, fill = C.white) {
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill },
    line: { color: fill === C.white ? C.line : fill, width: 0.75 }, shadow: shadow() });
}

async function cardHead(sl, x, y, Comp, color, text) {
  sl.addShape(pres.shapes.OVAL, { x, y, w: 0.4, h: 0.4, fill: { color }, line: { color, width: 1 } });
  sl.addImage({ data: await icon(Comp, C.white), x: x + 0.1, y: y + 0.1, w: 0.2, h: 0.2 });
  sl.addText(text, { x: x + 0.52, y: y - 0.02, w: 5, h: 0.44, fontFace: F, fontSize: S.cardHead, color: C.dark,
    valign: "middle", margin: 0, isTextBox: true });
}

// bullets: array of [boldLead, rest]
function bullets(sl, items, x, y, w, h, size = S.body, color = C.text) {
  const runs = [];
  items.forEach(([lead, rest], i) => {
    const last = i === items.length - 1;
    if (lead) runs.push({ text: lead + " ", options: { bold: true, bullet: true, color } });
    runs.push({ text: rest, options: { bullet: lead ? false : true, color, breakLine: !last } });
  });
  // pptxgenjs: bullet must be on the first run of each paragraph; continuation runs keep the paragraph
  const fixed = [];
  items.forEach(([lead, rest], i) => {
    const last = i === items.length - 1;
    if (lead) {
      fixed.push({ text: lead + " ", options: { bold: true, bullet: { indent: 14 }, color, paraSpaceAfter: 6 } });
      fixed.push({ text: rest, options: { color, breakLine: !last } });
    } else {
      fixed.push({ text: rest, options: { bullet: { indent: 14 }, color, paraSpaceAfter: 6, breakLine: !last } });
    }
  });
  sl.addText(fixed, { x, y, w, h, fontFace: F, fontSize: size, valign: "top", margin: 0, isTextBox: true });
}

function chips(sl, items, y = 1.4) {
  sl.addText("Tech", { x: 0.6, y, w: 0.6, h: 0.34, fontFace: F, fontSize: S.chip, bold: true, color: C.muted,
    valign: "middle", margin: 0, isTextBox: true });
  let x = 1.25;
  for (const t of items) {
    const w = 0.3 + 0.072 * t.length;
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.34, rectRadius: 0.17, fill: { color: C.chip },
      line: { color: C.chipLine, width: 0.5 } });
    sl.addText(t, { x, y, w, h: 0.34, fontFace: F, fontSize: S.chip, color: C.chipText, align: "center",
      valign: "middle", margin: 0, isTextBox: true });
    x += w + 0.1;
  }
}

function stat(sl, x, y, w, h, value, caption, color) {
  card(sl, x, y, w, h);
  sl.addText(value, { x, y: y + 0.22, w, h: 0.5, fontFace: F, fontSize: S.stat, color, align: "center",
    valign: "middle", margin: 0, isTextBox: true });
  sl.addText(caption, { x: x + 0.1, y: y + 0.76, w: w - 0.2, h: 0.5, fontFace: F, fontSize: S.caption, color: C.muted,
    align: "center", valign: "top", margin: 0, isTextBox: true });
}

function darkPanel(sl, x, y, w, h, label, lines) {
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: C.dark },
    line: { color: C.dark, width: 1 }, shadow: shadow() });
  sl.addText(label.toUpperCase(), { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: 0.3, fontFace: F, fontSize: S.label,
    color: C.orange, charSpacing: 3, margin: 0, isTextBox: true });
  sl.addText(lines.map((t, i) => ({ text: t, options: { breakLine: i < lines.length - 1, paraSpaceAfter: 4 } })),
    { x: x + 0.25, y: y + 0.55, w: w - 0.5, h: h - 0.7, fontFace: F, fontSize: S.algo, color: C.algo, valign: "top",
      margin: 0, isTextBox: true });
}

function banner(sl, x, y, w, h, label, runs) {
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: C.dark },
    line: { color: C.dark, width: 1 }, shadow: shadow() });
  if (label) sl.addText(label.toUpperCase(), { x: x + 0.3, y: y + 0.18, w: w - 0.6, h: 0.3, fontFace: F,
    fontSize: S.label, color: C.orange, charSpacing: 3, margin: 0, isTextBox: true });
  sl.addText(runs, { x: x + 0.3, y: y + (label ? 0.5 : 0.15), w: w - 0.6, h: h - (label ? 0.62 : 0.3), fontFace: F,
    fontSize: S.banner, color: C.white, valign: label ? "top" : "middle", margin: 0, isTextBox: true });
}

// table: header row + body rows; cells may be strings or run arrays; opts.boldFirst, opts.verdictCol
const border = { type: "solid", pt: 0.75, color: C.line };
function table(sl, header, rows, x, y, colW, rowH, opts = {}) {
  const fs = opts.fontSize || S.table;
  const head = header.map((t) => ({ text: t, options: { bold: false, color: C.white, fill: { color: C.dark },
    fontFace: F, fontSize: fs, valign: "middle", border: [border, border, border, border], margin: [4, 6, 4, 6] } }));
  const body = rows.map((r, ri) => r.map((cell, ci) => {
    const fill = ri % 2 ? C.rowAlt : C.white;
    const o = { fontFace: F, fontSize: fs, color: C.text, fill: { color: fill }, valign: "middle",
      border: [border, border, border, border], margin: [4, 6, 4, 6] };
    if (opts.boldFirst && ci === 0) o.bold = true;
    if (opts.centerCols && opts.centerCols.includes(ci)) o.align = "center";
    if (opts.numCol === ci) { o.color = C.green; o.align = "center"; }
    if (opts.verdictCol === ci) {
      const ex = cell === "Exceeded";
      o.fill = { color: ex ? C.exc : C.met }; o.color = ex ? C.excText : C.metText; o.bold = true; o.align = "center";
    }
    return { text: cell, options: o };
  }));
  sl.addTable([head, ...body], { x, y, colW, rowH, autoPage: false });
}

// cell helper: bold first line + "- " sub lines (as in the previous deck's feedback table)
const cellLines = (headLine, subs, boldHead = false) => [
  { text: headLine, options: { bold: boldHead, breakLine: subs.length > 0 } },
  ...subs.map((s, i) => ({ text: "   - " + s, options: { breakLine: i < subs.length - 1 } })),
];

// ------------------------------------------------------------------ slides
async function titleSlide(sl, { label, title, sub, meta }) {
  pageNo += 1;
  sl.background = { color: C.dark };
  sl.addShape(pres.shapes.OVAL, { x: 8.4, y: -1.6, w: 7.2, h: 7.2, fill: { color: C.green, transparency: 82 },
    line: { type: "none" } });
  sl.addShape(pres.shapes.OVAL, { x: 10.3, y: 3.9, w: 5.4, h: 5.4, fill: { color: C.orange, transparency: 85 },
    line: { type: "none" } });
  sl.addShape(pres.shapes.OVAL, { x: 7.2, y: 4.6, w: 3.0, h: 3.0, fill: { color: C.sage, transparency: 89 },
    line: { type: "none" } });
  sl.addShape(pres.shapes.OVAL, { x: 9.95, y: 2.1, w: 2.7, h: 2.7, fill: { color: C.green },
    line: { color: C.sage, width: 2 } });
  sl.addImage({ path: A("leaf.png"), x: 10.75, y: 2.9, w: 1.1, h: 1.1 });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 0.55, w: 1.9, h: 0.98, fill: { color: C.white }, line: { type: "none" } });
  sl.addImage({ path: A("pes_logo.png"), x: 0.9, y: 0.62, w: 1.7, h: 0.87 });
  sl.addText(label, { x: 0.8, y: 1.82, w: 9.0, h: 0.3, fontFace: F, fontSize: 12, color: C.orange, charSpacing: 3,
    margin: 0, isTextBox: true });
  sl.addText(title, { x: 0.8, y: 2.12, w: 8, h: 1.2, fontFace: F_LIGHT, fontSize: 66, color: C.white,
    margin: 0, isTextBox: true });
  if (sub) sl.addText(sub, { x: 0.8, y: 3.38, w: 7.6, h: 0.8, fontFace: F, fontSize: 20, color: C.algo, margin: 0,
    valign: "top", isTextBox: true });
  for (const [x, w, k, v] of meta || []) {
    sl.addText(k, { x, y: 5.3, w, h: 0.22, fontFace: F, fontSize: 10, color: C.sage, charSpacing: 3, margin: 0,
      isTextBox: true });
    sl.addText(v, { x, y: 5.6, w, h: 1.0, fontFace: F, fontSize: 16, color: C.white, margin: 0, valign: "top",
      isTextBox: true });
  }
}

async function build() {
  // 1 ---------------------------------------------------------------- title
  await titleSlide(pres.addSlide(), {
    label: "PROJECT PROGRESS REVIEW #3  ·  UE23CS441A PROJECT PHASE 3", title: "PlantIQ",
    sub: "Precision Coffee Agronomy, Multimodal Diagnostics\n& Spatial Marketplace",
    meta: [[0.8, 1.4, "PROJECT ID", "35"], [2.5, 2.6, "PROJECT GUIDE", "Prof. Deepti C"],
           [5.4, 4.2, "PROJECT TEAM", "Jeel Nada – PES2UG23CS357\nNidhi N – PES2UG23CS384\nMohammed Ayaan – PES2UG23AM058"]],
  });

  // 2 ---------------------------------------------------------------- outline
  {
    const sl = pres.addSlide(); base(sl, { label: "Overview", title: "Outline" });
    const items = [["Abstract & Scope", "The problem, gap and scope"], ["Review 1 & 2 Suggestions", "Remarks and progress"],
      ["Pipeline & Architecture", "Modules and integration"], ["Implementation Details", "Four modules, tech and algorithms"],
      ["Project Demonstration", "End-to-end demo video"], ["Test Plan & Strategy", "Methods, environment, tools"],
      ["Results & Discussion", "Expected vs actual, baselines"], ["Timeline & Conclusion", "Task status, achievements, roadmap"],
      ["References", "Literature and sources"]];
    items.forEach(([t, s], i) => {
      const x = 0.6 + (i % 3) * 4.14, y = 1.6 + Math.floor(i / 3) * 1.75;
      card(sl, x, y, 3.85, 1.45);
      const col = i % 2 ? C.orange : C.green;
      sl.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.4, w: 0.65, h: 0.65, fill: { color: col }, line: { color: C.white, width: 1 } });
      sl.addText(String(i + 1), { x: x + 0.25, y: y + 0.4, w: 0.65, h: 0.65, fontFace: F, fontSize: 20, color: C.white,
        align: "center", valign: "middle", margin: 0, isTextBox: true });
      sl.addText(t, { x: x + 1.1, y: y + 0.32, w: 2.65, h: 0.4, fontFace: F, fontSize: S.cardHead, color: C.dark, margin: 0, isTextBox: true });
      sl.addText(s, { x: x + 1.1, y: y + 0.74, w: 2.65, h: 0.4, fontFace: F, fontSize: S.caption, color: C.muted, margin: 0, isTextBox: true });
    });
  }

  // 3 ---------------------------------------------------------------- abstract & scope
  {
    const sl = pres.addSlide(); base(sl, { label: "Abstract & Scope", title: "The Problem Farmers Face" });
    card(sl, 0.6, 1.5, 5.95, 3.55); card(sl, 6.78, 1.5, 5.95, 3.55);
    await cardHead(sl, 0.85, 1.7, fa.FaSeedling, C.green, "Scattered Cultivation Knowledge");
    await cardHead(sl, 7.03, 1.7, fa.FaStore, C.orange, "Limited Market Visibility");
    bullets(sl, [[null, "Reliable information about sowing, irrigation schedules, pest control and harvesting is spread across many sources."],
      [null, "Content is often outdated, mostly in English, and not localized for Karnataka's crops and climate."],
      [null, "Farmers often rely on guesswork or on costly intermediaries for advice."]], 0.85, 2.35, 5.5, 2.6);
    bullets(sl, [[null, "Even after producing quality crops, farmers struggle to make their produce visible to buyers."],
      [null, "They often depend on middlemen, which can reduce their profits and bargaining power."],
      [null, "Direct buyer connections remain difficult to establish."]], 7.03, 2.35, 5.5, 2.6);
    banner(sl, 0.6, 5.3, 12.13, 1.55, "The gap and our scope", [
      { text: "Farmers lack one localized platform for cultivation decisions and crop visibility. " },
      { text: "PlantIQ", options: { color: C.orange } },
      { text: " (Android + web, self-hostable server) serves coffee growers in Chikkamagaluru, Kodagu and Hassan: leaf diagnosis, weather-aware advice grounded in 14 CCRI and research documents, an English/Kannada voice chatbot and a direct marketplace." }]);
  }

  // 4 ---------------------------------------------------------------- suggestions
  {
    const sl = pres.addSlide(); base(sl, { label: "Feedback & Progress", title: "Suggestions from Review 1 & 2" });
    const rows = [
      ["1", cellLines("Enhance local language integration", ["Now the local language translation to Kannada is seamless and smooth"]),
        cellLines("High", ["Already implemented", "Uses local STT model"]),
        cellLines("Kannada works end to end.", ["Kannada-script replies in 17/17 test chats", "Kannada retrieval Recall@3 0.905 (dense RAG 0.095)"], true)],
      ["2", cellLines("RAG — CNN Integration", ["Input structured standardized"]),
        cellLines("High", ["Standard input format"]),
        cellLines("Standardized input structure.", ["Diagnosis, confidence and weather in one prompt", "Weak evidence marks a result as uncertain"], true)],
      ["3", cellLines("Testing with actual subjects", ["Testing with subjects with knowledge in this field."]),
        cellLines("Medium", ["Requires field co-ordination."]),
        cellLines("Initial field testing completed.", ["Feedback collected from coffee planters.", "Positive response on usability."], true)],
      ["4", cellLines("Testing Newly trained CNN model", ["90% Validation Set, 80% on new leaf"]),
        cellLines("High", ["Model training completed", "Testing pipeline in place"]),
        cellLines("Leak-free evaluation done.", ["Dataset audit: 58,549 images are 861 leaf patches", "Group 5-fold CV: 97.9% accuracy, macro-F1 0.970"], true)],
      ["5", cellLines("Streamlining Integration flow", ["Project completely integrated"]),
        cellLines("High", ["All modules implemented and integrated", "End-to-end flow tested"]),
        cellLines("Complete system integration.", ["CNN + RAG + Chatbot + Market Discovery", "373/373 automated tests pass"], true)],
    ];
    table(sl, ["#", "Suggestion / Remark", "Feasibility", "Progress Shown"], rows, 0.6, 1.45, [0.55, 4.35, 2.55, 4.68],
      [0.42, 0.98, 0.98, 0.98, 0.98, 0.98], { numCol: 0 });
  }

  // 5 ---------------------------------------------------------------- architecture
  {
    const sl = pres.addSlide(); base(sl, { label: "System Design", title: "Pipeline & Architecture", dark: true });
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.5, w: 12.13, h: 5.0, rectRadius: 0.08,
      fill: { color: "111111" }, line: { color: "2A4936", width: 0.75 } });
    sl.addImage({ path: A("architecture.png"), x: 0.75, y: 1.6, w: 11.83, h: 4.84 });
    sl.addText("Client & Inputs  →  Perception & Processing  →  AI Reasoning & Advisory  →  Storage & Outcomes",
      { x: 0.6, y: 6.6, w: 12.13, h: 0.35, fontFace: F, fontSize: S.body, color: C.algo, align: "center", margin: 0, isTextBox: true });
  }

  // module slide builder
  async function moduleSlide({ label, title, tech, impl, stats, formulas, algo, extra }) {
    const sl = pres.addSlide(); base(sl, { label, title });
    chips(sl, tech);
    card(sl, 0.6, 1.95, 5.95, 3.4);
    await cardHead(sl, 0.85, 2.1, fa.FaCode, C.green, "Implementation");
    bullets(sl, impl, 0.85, 2.65, 5.5, 2.6, 12.5);
    stats.forEach(([v, c], i) => stat(sl, 0.6 + i * 2.035, 5.5, 1.88, 1.4, v, c, i === 1 ? C.orange : C.green));
    if (formulas) {
      card(sl, 6.8, 1.95, 5.93, 2.2);
      await cardHead(sl, 7.05, 2.1, fa.FaScaleBalanced, C.orange, "Key formulas");
      sl.addText(formulas.map(([k, v], i) => [{ text: k + "  ", options: { bold: true, paraSpaceAfter: 6 } },
        { text: v, options: { breakLine: i < formulas.length - 1 } }]).flat(),
        { x: 7.05, y: 2.65, w: 5.5, h: 1.4, fontFace: F, fontSize: 12.5, color: C.text, valign: "top", margin: 0, isTextBox: true });
      darkPanel(sl, 6.8, 4.35, 5.93, 2.55, "Algorithm", algo);
    } else {
      darkPanel(sl, 6.8, 1.95, 5.93, 2.55, "Algorithm", algo);
    }
    if (extra) await extra(sl);
    return sl;
  }

  // 6 ---------------------------------------------------------------- module 1
  await moduleSlide({
    label: "Module 1", title: "Leaf Pathology Computer Vision (CNN)",
    tech: ["PyTorch", "ResNet-50", "CUDA", "SHA-256 cache", "Upload sanitiser", "PostgreSQL / SQLite"],
    impl: [["Fine-tuned ResNet-50:", "head replaced by Dropout(0.4) → Linear(2048→5). Classes: leaf miner, leaf rust, Phoma leaf spot, Cercospora and healthy."],
      ["Upload guard:", "file-signature check, size and pixel limits, EXIF and GPS removed, re-encoded as JPEG before inference."],
      ["SHA-256 cache", "over (image + user + language + query) answers repeat requests in under 1 ms."],
      ["Confidence gate:", "below 75%, or when the best retrieved passage scores under 0.60, the result is marked uncertain and the grower is asked to check more leaves."]],
    stats: [["5", "foliar classes"], ["224×224", "input resolution"], ["75%", "confidence gate"]],
    formulas: [["Softmax:", "P(c) = exp(z_c) / Σ exp(z_i)"], ["Residual skip:", "H(x) = F(x) + x  (prevents vanishing gradients)"],
      ["Uncertain if:", "conf < 75%  or  (disease and evidence < 0.60)"]],
    algo: ["1. img = sanitise(upload)", "2. hash = SHA256(img + uid + lang + query); if cached → return",
      "3. tensor = Normalize(Resize(img, 224×224))", "4. probs = Softmax(ResNet50(tensor))",
      "5. class, conf = argmax(probs), max(probs)×100", "6. mark uncertain if gate fails; cache and return"],
  });

  // 7 ---------------------------------------------------------------- module 2
  await moduleSlide({
    label: "Module 2", title: "Hybrid RAG & Agronomic Advisory Engine",
    tech: ["bge-m3 (1024-d)", "FAISS", "BM25", "bge-reranker-v2-m3", "Gemini 2.5 Flash", "Groq gpt-oss-120b", "Open-Meteo API"],
    impl: [["Live microclimate", "from Open-Meteo feeds a rule-based infection risk and a 3-day spray window. If GPS is missing, no weather is made up."],
      ["Hybrid retrieval:", "dense + BM25 (top 20 each) → RRF → cross-encoder rerank → +0.1 for the diagnosed disease → near-duplicates dropped → top 3."],
      ["LLM call:", "Gemini 2.5 Flash, Groq as failover, built-in offline guide if both fail."],
      ["Dosage audit:", "every dose, including words like “four litres”, must appear in the retrieved CCRI text (“Verified” vs “Check doses”)."]],
    stats: [["1024-d", "dense embeddings (bge-m3, GPU)"], ["Top 3", "chunks after rerank (from 20 + 20)"], ["k = 60", "RRF constant"]],
    formulas: [["RRF:", "1/(60 + dense_rank) + 1/(60 + sparse_rank)"], ["Sigmoid:", "1 / (1 + e^(−z))"],
      ["Risk:", "high when humidity ≥ 80% and 20–28 °C; spray window = first day with rain < 40% and < 2 mm"]],
    algo: ["1. route question → one English search question", "2. dense + BM25, top 20 each; fuse with RRF",
      "3. rerank with cross-encoder + sigmoid; +0.1 on disease topic", "4. drop near-duplicates (Jaccard ≥ 0.8) → top 3",
      "5. prompt = disease + weather + chunks + question", "6. answer = LLM(Gemini → Groq → offline); audit doses"],
  });

  // 8 ---------------------------------------------------------------- module 3
  await moduleSlide({
    label: "Module 3", title: "Multimodal Chatbot & Linguistic Pre-Router",
    tech: ["IndicConformer-600M", "Svarah Whisper", "Groq Whisper", "Gemini Audio", "Kannada Unicode regex", "PostgreSQL"],
    impl: [["Language router:", "an LLM rewrites each message as one English search question and sets the reply language. It also sees the last 2 exchanges, so follow-ups like “what pH should it have?” resolve."],
      ["Voice (3-tier STT):", "IndicConformer (Kannada) / Svarah Whisper (English) → Groq Whisper → Gemini Audio."],
      ["Context fusion:", "last 8 chat turns, live weather, CNN diagnosis of a photo or past scan, and RAG chunks in one prompt."],
      ["Photos", "are stored as sanitised JPEGs with a media ID, so threads and images persist across sessions."]],
    stats: [["< 1 ms", "Kannada script detection"], ["3 tiers", "speech-to-text fallback"], ["8 turns", "chat context window"]],
    algo: ["1. if audio: M = STT_Cascade(resample 16 kHz)", "2. route(M, last 2 exchanges) → script, English_query, lang",
      "3. weather = OpenMeteo(GPS or typed coords); diag = ResNet50(photo)", "4. chunks = RAG.search(English_query, k=3); skip for greetings",
      "5. prompt = history(8) + weather + diag + chunks + lang rule", "6. reply = Gemini → Groq → offline card; save thread"],
    extra: async (sl) => {
      card(sl, 6.8, 4.7, 5.93, 2.2);
      sl.addText("SPEECH-TO-TEXT FALLBACK CHAIN", { x: 7.05, y: 4.86, w: 5.4, h: 0.3, fontFace: F, fontSize: S.label,
        color: C.orange, charSpacing: 3, margin: 0, isTextBox: true });
      const steps = [["PRIMARY", "Local Model", "local GPU / CPU", true], ["FAILOVER 1", "Groq Whisper", "whisper-large-v3", false],
        ["FAILOVER 2", "Gemini Audio", "cloud API", false]];
      steps.forEach(([k, t, s, primary], i) => {
        const x = 7.05 + i * 1.92;
        sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.35, w: 1.55, h: 1.2, rectRadius: 0.06,
          fill: { color: primary ? C.green : C.chip }, line: { color: primary ? C.green : C.chipLine, width: 0.75 } });
        sl.addText([{ text: k, options: { fontSize: 9, charSpacing: 2, color: primary ? C.algo : C.muted, breakLine: true } },
          { text: t, options: { fontSize: 13, color: primary ? C.white : C.dark, breakLine: true } },
          { text: s, options: { fontSize: 10, color: primary ? C.algo : C.muted } }],
          { x, y: 5.35, w: 1.55, h: 1.2, fontFace: F, align: "center", valign: "middle", margin: 2, isTextBox: true });
        if (i < 2) sl.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.6, y: 5.83, w: 0.28, h: 0.24, fill: { color: C.orange }, line: { type: "none" } });
      });
    },
  });

  // 9 ---------------------------------------------------------------- module 4
  await moduleSlide({
    label: "Module 4", title: "Direct Spatial Crop Marketplace",
    tech: ["FastAPI", "SQLAlchemy", "PostgreSQL / SQLite", "Haversine", "Capacitor Android Intents", "Google Maps URL", "WhatsApp (wa.me)"],
    impl: [["Direct listings:", "grower to buyer, with no commission or intermediary. A listing holds variety, quantity, price, contact and up to 8 captioned photos."],
      ["Unit normalisation:", "the server converts bags, quintals and tonnes to kg and prices to Rs/kg, so lots compare fairly."],
      ["Discovery:", "keyword search; filters for variety, lot size, Rs/kg range, distance (15 to 120 km) and photos; 5 sort orders."],
      ["One-tap actions:", "Google Maps route, tel: dialer and pre-filled WhatsApp. Owner-only edits, 50 listings per user."]],
    stats: [["Haversine", "distance sorting"], ["1-tap", "call, chat, navigate"], ["Rs/kg", "normalised lot prices"]],
    formulas: [["Haversine:", "d = 2R · arcsin(√(sin²(Δlat/2) + cos(lat₁)·cos(lat₂)·sin²(Δlng/2)))"],
      ["Earth radius:", "R = 6371 km"], ["Normalise:", "qty_kg = qty × unit_kg;  price_kg = price / unit_kg"]],
    algo: ["1. validate price > 0, qty > 0, phone valid", "2. qty_kg, price_kg = normalise(units)",
      "3. photos = sanitised JPEGs + captions", "4. save CropListing to DB",
      "5. filter; distance = Haversine(buyer, listing)", "6. sort; build Maps and wa.me links"],
  });

  // 10 --------------------------------------------------------------- demo
  {
    const sl = pres.addSlide();
    base(sl, { label: "Live Walkthrough", title: "Project Demonstration",
      subtitle: "Full pipeline: image → diagnosis → weather + RAG advisory → chatbot → marketplace" });
    sl.addImage({ path: A("demo_screen.png"), x: 0.6, y: 1.77, w: 2.67, h: 4.66,
      sizing: { type: "cover", w: 2.67, h: 4.66 } });
    card(sl, 8.22, 1.55, 4.51, 5.3);
    sl.addShape(pres.shapes.OVAL, { x: 8.55, y: 1.8, w: 0.4, h: 0.4, fill: { color: C.green }, line: { color: C.green, width: 1 } });
    sl.addImage({ data: await icon(fa.FaListUl, C.white), x: 8.65, y: 1.9, w: 0.2, h: 0.2 });
    const steps = [["Sign in", "Register and log in"], ["Scan a leaf", "CNN diagnosis with confidence"],
      ["Get advice", "Live weather, RAG advisory, dosage audit"], ["Ask in Kannada", "Voice or text chat with scan context"],
      ["List and sell", "Crop listing, Maps and WhatsApp"]];
    steps.forEach(([t, s], i) => {
      const y = 2.45 + i * 0.85, col = i % 2 ? C.orange : C.green;
      sl.addShape(pres.shapes.OVAL, { x: 8.55, y, w: 0.4, h: 0.4, fill: { color: col }, line: { color: col, width: 1 } });
      sl.addText(String(i + 1), { x: 8.55, y, w: 0.4, h: 0.4, fontFace: F, fontSize: 13, color: C.white, align: "center", valign: "middle", margin: 0, isTextBox: true });
      sl.addText(t, { x: 9.2, y: y - 0.08, w: 3.3, h: 0.3, fontFace: F, fontSize: S.cardHead, color: C.dark, margin: 0, isTextBox: true });
      sl.addText(s, { x: 9.2, y: y + 0.24, w: 3.3, h: 0.28, fontFace: F, fontSize: S.caption, color: C.muted, margin: 0, isTextBox: true });
    });
  }

  // 11 --------------------------------------------------------------- test plan 1
  {
    const sl = pres.addSlide(); base(sl, { label: "Test Plan & Strategy", title: "Testing Activities, Timeline & Methods" });
    sl.addText("8-week timeline, 4 sprints, plus the comparison study", { x: 0.6, y: 1.25, w: 6, h: 0.3, fontFace: F, fontSize: S.cardHead, color: C.dark, margin: 0, isTextBox: true });
    table(sl, ["Sprint", "Weeks", "Activity"], [
      ["1", "1–2", "Unit tests per module: ResNet-50 weights (SHA-256) and head, FAISS/BM25 index, router, schemas"],
      ["2", "3–4", "Integration (API + database) and functional journeys: scan → advisory → chat, marketplace CRUD"],
      ["3", "5–6", "Frontend unit and component tests (Vitest); end-to-end UI at a Pixel 7 viewport (Playwright)"],
      ["4", "7–8", "Security (auth, tokens, SQLi, XSS, prompt injection), performance and real-model runs"],
      ["5", "Nov", "Comparison with re-implemented baselines; fixes for faults it found, with regression tests"],
    ], 0.6, 1.65, [0.75, 0.8, 4.3], [0.42, 0.76, 0.76, 0.76, 0.76, 0.76], { numCol: 0, centerCols: [1] });
    sl.addText("Test methods and why", { x: 6.75, y: 1.25, w: 6, h: 0.3, fontFace: F, fontSize: S.cardHead, color: C.dark, margin: 0, isTextBox: true });
    table(sl, ["Method", "Tests", "Why"], [
      ["Unit (backend)", "162", "Isolates faults to one function or service"],
      ["Integration + functional", "74", "API, database and multi-step journeys verified together"],
      ["Security", "59", "Accounts, uploads and spray advice: a wrong answer can cause harm"],
      ["Non-functional + real model", "14", "Latency, load and limits; real CNN weights and bge-m3 index"],
      ["Frontend unit + component", "52", "UI logic and English/Kannada strings"],
      ["End-to-end UI", "12", "The whole app in a phone browser"],
    ], 6.75, 1.65, [2.2, 0.7, 3.08], [0.42, 0.63, 0.63, 0.63, 0.63, 0.63, 0.63], { centerCols: [1] });
    banner(sl, 0.6, 6.25, 12.13, 0.66, null, [{ text: "373 / 373", options: { fontSize: 22, color: C.white } },
      { text: "  automated tests passed (100%): pytest, Vitest and Playwright", options: { color: C.algo } }]);
  }

  // 12 --------------------------------------------------------------- test plan 2
  {
    const sl = pres.addSlide(); base(sl, { label: "Test Plan & Strategy", title: "Test Environment, Roles & Tools" });
    sl.addText("Roles", { x: 0.6, y: 1.25, w: 3, h: 0.3, fontFace: F, fontSize: S.cardHead, color: C.dark, margin: 0, isTextBox: true });
    table(sl, ["Member", "Module", "Test responsibility"], [
      ["Ayaan", "CNN", "44 tests: weights, preprocessing, softmax, cache, corrupted input, 75% gate"],
      ["Jeel", "RAG + weather", "55 tests: zero-mock weather, risk, FAISS/BM25, RRF, rerank, dose audit"],
      ["Nidhi", "Chatbot + Marketplace", "125 tests: routing, history, Kannada, voice; listings, units, Haversine, links"],
      ["All three", "Platform + security", "149 tests: auth, tokens, 403 isolation, injection, uploads, UI"],
    ], 0.6, 1.62, [1.05, 1.75, 4.65], [0.4, 0.58, 0.58, 0.58, 0.58], { boldFirst: true });
    sl.addText("Tools (all open-source)", { x: 0.6, y: 4.5, w: 5, h: 0.3, fontFace: F, fontSize: S.cardHead, color: C.dark, margin: 0, isTextBox: true });
    table(sl, ["Tool", "Role"], [
      ["pytest + FastAPI TestClient", "Backend runner, in-memory API tests"],
      ["Vitest, Playwright", "Frontend components; end-to-end UI"],
      ["PyTorch, FAISS, rank_bm25, Pillow", "Model, index and corrupted-image checks"],
      ["Jupyter, scikit-learn, SciPy", "Comparison study: group folds, bootstrap, McNemar, Wilcoxon"],
    ], 0.6, 4.87, [3.1, 4.35], [0.36, 0.42, 0.42, 0.42, 0.42], { boldFirst: true, fontSize: 11 });
    card(sl, 8.3, 1.25, 4.43, 2.45);
    await cardHead(sl, 8.55, 1.42, fa.FaServer, C.green, "Test environment");
    bullets(sl, [[null, "Windows 11, RTX 3070 Laptop GPU (8 GB, CUDA 12), Python 3.11"],
      [null, "PostgreSQL or SQLite; deterministic fake models so the fast suite runs without a GPU"],
      [null, "Gemini → Groq fallback for LLM calls"]], 8.55, 1.97, 4.0, 1.65, 12);
    card(sl, 8.3, 3.9, 4.43, 3.0);
    await cardHead(sl, 8.55, 4.07, fa.FaCircleCheck, C.green, "Benefits and drawbacks");
    bullets(sl, [["Fast:", "305 backend tests run in about 30 s."],
      ["Found real bugs:", "a history-blind chat router, Kannada words taken as weather questions, a topic filter that dropped answers."],
      ["Drawbacks:", "real-model tests need an NVIDIA GPU; LLM free-tier limits; leaf images come from one public dataset."]],
      8.55, 4.62, 4.0, 2.2, 12);
  }

  // 13 --------------------------------------------------------------- results 1
  {
    const sl = pres.addSlide(); base(sl, { label: "Results & Discussion", title: "Expected vs. Actual Results" });
    table(sl, ["Metric", "Target", "Actual", "Verdict"], [
      ["Test pass rate", "all pass", "373/373", "Met"],
      ["CNN accuracy (leak-free)", "≥ 90%", "97.9% (macro-F1 0.970)", "Exceeded"],
      ["Retrieval Recall@3", "beat dense RAG", "0.867 vs 0.500", "Met"],
      ["Unsupported doses", "0", "0% (LLM alone: 20.4%)", "Met"],
      ["Kannada replies", "Kannada script", "17/17 test chats", "Met"],
      ["Cross-user access", "blocked", "403 / 401 on tested routes", "Met"],
      ["Cache hit speed", "< 5 ms", "0.85 ms", "Exceeded"],
    ], 0.6, 1.6, [2.3, 1.55, 2.45, 1.2], [0.5, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7], { boldFirst: true, verdictCol: 3 });
    card(sl, 8.4, 1.6, 4.33, 5.4);
    await cardHead(sl, 8.65, 1.78, fa.FaLightbulb, C.orange, "Deviations and reasons");
    bullets(sl, [["Dataset leakage:", "JMuBEN's 58,549 images are 861 leaf patches; a random split leaks 99.96% of test images, so all models were re-run on leak-free folds."],
      ["Baselines slightly ahead:", "GoogLeNet 0.988 and YOLOv8 0.985 macro-F1 vs 0.970 for our ResNet-50."],
      ["Faults found and fixed:", "a hard topic filter dropped answers (Recall@3 0.813 → 0.867); the chat router ignored history (follow-ups 0.80 → 0.90)."],
      ["CNN cold start", "is 704 ms (CUDA start-up); later calls take 5.3 ms on the GPU."]], 8.65, 2.33, 3.9, 4.55, 12.5);
  }

  // 14 --------------------------------------------------------------- results 2 (measured comparison)
  {
    const sl = pres.addSlide(); base(sl, { label: "Results & Discussion", title: "Comparison with Existing Approaches" });
    table(sl, ["Module", "Compared with", "Metric", "PlantIQ", "Baseline"], [
      ["CNN", "GoogLeNet TL [1]", "Macro-F1", "0.970", "0.988"],
      ["CNN", "YOLOv8s-cls [2]", "Macro-F1", "0.970", "0.985"],
      ["Retrieval", "Dense LangChain RAG [2]", "Recall@3, 75 Q", "0.867", "0.500"],
      ["Retrieval (Kannada)", "Dense LangChain RAG [2]", "Recall@3, 21 Q", "0.905", "0.095"],
      ["Advisory answers", "Dense RAG / no retrieval", "Correct, 54 Q", "0.944", "0.824 / 0.611"],
      ["Chatbot", "LangChain chatbot [2]", "Expected, 43 chats", "43/43", "15/43"],
    ], 0.6, 1.6, [1.6, 2.05, 1.5, 0.85, 1.25], [0.45, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6], { boldFirst: true, centerCols: [3, 4] });
    card(sl, 8.15, 1.6, 4.58, 4.05);
    sl.addChart(pres.charts.BAR, [
      { name: "PlantIQ", labels: ["Recall@3", "Kannada R@3", "Answers", "Chatbot"], values: [0.867, 0.905, 0.944, 0.91] },
      { name: "Baseline", labels: ["Recall@3", "Kannada R@3", "Answers", "Chatbot"], values: [0.5, 0.095, 0.824, 0.38] },
    ], { x: 8.3, y: 1.72, w: 4.3, h: 3.85, barDir: "col", barGrouping: "clustered", chartColors: [C.green, C.orange],
      showTitle: true, title: "PlantIQ vs re-implemented baselines", titleFontFace: F, titleFontSize: 12, titleColor: C.dark,
      showLegend: true, legendPos: "b", legendFontFace: F, legendFontSize: 10, legendColor: C.text,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontFace: F, dataLabelFontSize: 9, dataLabelColor: C.text,
      dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 1, valAxisHidden: true, valGridLine: { style: "none" },
      catAxisLabelFontFace: F, catAxisLabelFontSize: 10, catAxisLabelColor: C.muted, catGridLine: { style: "none" } });
    banner(sl, 0.6, 5.95, 12.13, 0.95, "Same data, same language model", [
      { text: "Baselines re-implemented from [1] and [2]. The lighter CNNs win on accuracy; PlantIQ wins on grounding, Kannada and conversation.", options: { fontSize: 14 } }]);
  }

  // 15 --------------------------------------------------------------- timeline (new, template slide 10)
  {
    const sl = pres.addSlide(); base(sl, { label: "Timeline", title: "Timeline — Update on Tasks" });
    const ms = [["Phase 1", "Reviews 1 & 2", "Problem, literature survey, requirements and design"],
      ["Phase 2", "Prototypes", "CNN, RAG advisory, chatbot and marketplace modules"],
      ["Phase 3", "Up to 25 Oct", "Integration, security hardening, Android APK, 354 tests"],
      ["Review 3", "28 Oct", "Complete system with all four modules demonstrated"],
      ["21–22 Nov", "Comparison", "Re-implemented baselines; RAG and chatbot fixes; 373 tests"],
      ["22–23 Nov", "Documentation", "IEEE paper (full and short) and project summary"]];
    sl.addShape(pres.shapes.LINE, { x: 0.95, y: 2.35, w: 11.4, h: 0, line: { color: C.sage, width: 2 } });
    for (let i = 0; i < ms.length; i++) {
      const [when, what, desc] = ms[i];
      const x = 0.6 + i * 2.045, col = i % 2 ? C.orange : C.green;
      sl.addShape(pres.shapes.OVAL, { x: x + 0.62, y: 2.1, w: 0.5, h: 0.5, fill: { color: col }, line: { color: C.white, width: 1.5 } });
      sl.addImage({ data: await icon(fa.FaCheck, C.white), x: x + 0.745, y: 2.225, w: 0.25, h: 0.25 });
      card(sl, x, 2.85, 1.88, 2.55);
      sl.addText(when.toUpperCase(), { x: x + 0.15, y: 3.0, w: 1.6, h: 0.28, fontFace: F, fontSize: 10, color: C.orange, charSpacing: 2, margin: 0, isTextBox: true });
      sl.addText(what, { x: x + 0.15, y: 3.3, w: 1.6, h: 0.35, fontFace: F, fontSize: S.cardHead, color: C.dark, margin: 0, isTextBox: true });
      sl.addText(desc, { x: x + 0.15, y: 3.72, w: 1.6, h: 1.2, fontFace: F, fontSize: 12, color: C.text, valign: "top", margin: 0, isTextBox: true });
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: 4.95, w: 1.1, h: 0.3, rectRadius: 0.15, fill: { color: C.met }, line: { type: "none" } });
      sl.addText("Completed", { x: x + 0.15, y: 4.95, w: 1.1, h: 0.3, fontFace: F, fontSize: 10, bold: true, color: C.metText, align: "center", valign: "middle", margin: 0, isTextBox: true });
    }
    banner(sl, 0.6, 5.75, 12.13, 1.1, "Status", [{ text: "All planned tasks are complete. Since Review 3 the work has been evaluation and documentation; the paper is " },
      { text: "under review", options: { color: C.orange } }, { text: "." }]);
  }

  // 16 --------------------------------------------------------------- conclusion
  {
    const sl = pres.addSlide(); base(sl, { label: "Conclusion & Future Work", title: "Conclusion" });
    banner(sl, 0.6, 1.4, 12.13, 0.9, null, [{ text: "PlantIQ", options: { color: C.orange } },
      { text: " is a single pipeline for coffee growers: photograph a leaf, get a grounded treatment plan in their own language, and sell the harvest directly." }]);
    const flow = ["Leaf image", "ResNet-50 diagnosis", "Weather + hybrid RAG", "Kannada/English chat", "Direct marketplace"];
    flow.forEach((t, i) => {
      const x = 0.6 + i * 2.5;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.5, w: 2.15, h: 0.55, rectRadius: 0.27, fill: { color: i % 2 ? "FBE6C8" : C.chip }, line: { color: i % 2 ? "F2C48F" : C.chipLine, width: 0.75 } });
      sl.addText(t, { x, y: 2.5, w: 2.15, h: 0.55, fontFace: F, fontSize: 12.5, color: C.dark, align: "center", valign: "middle", margin: 0, isTextBox: true });
      if (i < 4) sl.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.17, y: 2.65, w: 0.3, h: 0.25, fill: { color: C.orange }, line: { type: "none" } });
    });
    table(sl, ["Module", "What we achieved"], [
      ["CNN", "ResNet-50 for 5 leaf conditions with a 75% confidence gate and SHA-256 cache; 97.9% accuracy on leak-free folds."],
      ["RAG", "Dense + BM25 + RRF + cross-encoder with live weather and a dose audit; Recall@3 0.867 vs 0.500, no unsupported doses."],
      ["Chatbot", "Kannada, Kanglish and English with voice, a history-aware router and scan hand-off; 43/43 test chats."],
      ["Marketplace", "Direct listings with unit normalisation, Haversine sorting, Maps and one-tap call or WhatsApp."],
    ], 0.6, 3.3, [1.3, 6.35], [0.4, 0.62, 0.62, 0.62, 0.62], { boldFirst: true, fontSize: 11 });
    card(sl, 8.5, 3.3, 4.23, 1.2);
    sl.addText("373/373", { x: 8.6, y: 3.42, w: 1.75, h: 0.95, fontFace: F, fontSize: 28, color: C.green, align: "center", valign: "middle", margin: 0, isTextBox: true });
    sl.addText("automated tests passed: unit, integration, security, frontend and end-to-end", { x: 10.35, y: 3.42, w: 2.25, h: 0.95, fontFace: F, fontSize: S.caption, color: C.muted, valign: "middle", margin: 0, isTextBox: true });
    card(sl, 8.5, 4.65, 4.23, 2.25);
    sl.addText("KEY TAKEAWAYS", { x: 8.75, y: 4.8, w: 3.8, h: 0.28, fontFace: F, fontSize: S.label, color: C.orange, charSpacing: 3, margin: 0, isTextBox: true });
    bullets(sl, [[null, "Grounding in CCRI text cut unsupported doses from 20% of answers to none."],
      [null, "Routing Kannada to English search raised Kannada retrieval from 0.095 to 0.905."],
      [null, "A leak-free test exposed duplicated data that inflates accuracy."]], 8.75, 5.15, 3.85, 1.7, 12);
    sl.addText("PlantIQ supports a grower from a sick leaf to an informed treatment decision (confirm with an agronomist) to a direct sale, in their own language.",
      { x: 0.6, y: 6.4, w: 7.7, h: 0.55, fontFace: F, fontSize: 12, italic: true, color: C.dark, margin: 0, isTextBox: true });
  }

  // 17 --------------------------------------------------------------- future scope
  {
    const sl = pres.addSlide();
    base(sl, { label: "Conclusion & Future Work", title: "Future Scope & Roadmap",
      subtitle: "From a server-dependent assistant to a field-ready, sensor-aware, transaction-capable platform" });
    table(sl, ["Module", "Planned upgrade", "What it changes"], [
      ["CNN + System", "Offline-first: INT8 ONNX model on-device plus CRDT sync", "The 94 MB model shrinks to about 24 MB and runs on the phone; diagnosis works without network and syncs on Wi-Fi."],
      ["Evaluation", "Field photo test set from Karnataka estates; grower study; speech WER", "Measures accuracy on real field photos and real Kannada speech, which public data does not cover."],
      ["RAG", "Graph-RAG knowledge graph (Neo4j / NetworkX) [8]", "Answers multi-constraint questions by traversing disease → control → restriction → cultivar links."],
      ["Environment", "On-farm LoRaWAN leaf-wetness and microclimate sensors", "Sub-acre readings and leaf wetness duration replace grid-level weather in the risk index."],
      ["Marketplace", "ONDC integration with UPI escrow", "Moves from contact on WhatsApp to a full trade with payment held until delivery."],
    ], 0.6, 1.6, [1.6, 3.6, 6.93], [0.42, 0.6, 0.6, 0.6, 0.6, 0.6], { boldFirst: true });
    const terms = [["Near term", "On-device INT8 model; field test set", C.green], ["Mid term", "Severity grading, offline sync, ONDC pilot", C.orange],
      ["Long term", "Graph-RAG, LoRaWAN sensors, drone NDVI surveying", C.brown]];
    terms.forEach(([k, t, col], i) => {
      const x = 0.6 + i * 4.14;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.45, w: 3.85, h: 1.05, rectRadius: 0.08, fill: { color: col }, line: { type: "none" }, shadow: shadow() });
      sl.addText([{ text: k.toUpperCase(), options: { fontSize: S.label, charSpacing: 3, color: "F6E3C7", breakLine: true } },
        { text: t, options: { fontSize: 14, color: C.white } }], { x: x + 0.2, y: 5.45, w: 3.45, h: 1.05, fontFace: F, valign: "middle", margin: 0, isTextBox: true });
    });
    sl.addText("Works offline, grades severity, reasons over agronomic constraints, and closes the sale with secure payment.",
      { x: 0.6, y: 6.62, w: 12.13, h: 0.35, fontFace: F, fontSize: 12, italic: true, color: C.dark, align: "center", margin: 0, isTextBox: true });
  }

  // 18 --------------------------------------------------------------- references (IEEE format, same list as the paper)
  {
    const sl = pres.addSlide(); base(sl, { label: "Sources", title: "References" });
    card(sl, 0.6, 1.45, 12.13, 5.45);
    const refs = [
      "K. S. Anudeep, K. M. Prajwal, H. Sireesh Gowda, G. N. Venkatesh Prasad, and G. Jagadamba, “Coffee leaf disease detection using convolution neural network,” Grenze Int. J. Eng. Technol., vol. 10, no. 2, Jun. 2024.",
      "S. Selva Kumar, I. A. Banday, V. V. Shanbhag, A. K. M. A. Khan, and M. Gada, “Overcoming LLM challenges using RAG-driven precision in coffee leaf disease remediation,” in Proc. ICETCS, Bengaluru, India, 2024.",
      "S. Patil, J. Devasia, G. Daniel, and N. Surya Prakash Rao, “Influence of elevation and rainfall on leaf growth, bean characteristics and yield components of coffee,” J. Plantation Crops, vol. 50, no. 2, pp. 78-84, 2022.",
      "N. Singh et al., “Farmer.Chat: Scaling AI-powered agricultural services for smallholder farmers,” arXiv:2409.08916, 2024.",
      "R. Sapkota et al., “Multi-modal LLMs in agriculture: A comprehensive review,” preprint, 2024.",
      "K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image recognition,” in Proc. IEEE CVPR, 2016, pp. 770-778.",
      "P. Lewis et al., “Retrieval-augmented generation for knowledge-intensive NLP tasks,” in Proc. NeurIPS, vol. 33, 2020, pp. 9459-9474.",
      "X. Zhao et al., “Implementation of large language models and agricultural knowledge graphs for efficient plant disease detection,” Agriculture, vol. 14, no. 8, p. 1359, 2024.",
      "C. S. Santhosha and K. K. Umesh, “An ensemble approach for coffee crop yield prediction based on agronomic factors,” ASEAN Eng. J., vol. 13, no. 3, pp. 29-38, 2023.",
      "A. L. S. Xavier, B. J. T. Fernandes, and J. F. L. de Oliveira, “A hybrid swarm-based system for commodity price forecasting during the Covid-19 pandemic,” IEEE Access, vol. 11, 2023.",
      "J. Jepkoech, D. M. Mugo, B. K. Kenduiywo, and E. C. Too, “Arabica coffee leaf images dataset for coffee leaf disease detection and classification,” Data in Brief, vol. 36, p. 107142, 2021.",
    ];
    sl.addText(refs.map((r, i) => [{ text: `[${i + 1}]  `, options: { color: C.orange, paraSpaceAfter: 5 } },
      { text: r, options: { color: C.text, breakLine: i < refs.length - 1 } }]).flat(),
      { x: 0.85, y: 1.62, w: 11.65, h: 5.2, fontFace: F, fontSize: S.table, valign: "top", margin: 0, isTextBox: true });
  }

  // 19 --------------------------------------------------------------- thank you
  await titleSlide(pres.addSlide(), { label: "PLANTIQ  ·  PROJECT PROGRESS REVIEW #3", title: "Thank You",
    sub: "Questions & Discussion" });

  await pres.writeFile({ fileName: OUT });
  console.log("wrote", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
