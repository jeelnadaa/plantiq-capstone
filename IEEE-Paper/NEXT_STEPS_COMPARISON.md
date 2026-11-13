# PlantIQ IEEE paper: what to do next

The paper is in [main.tex](main.tex), compiled to [main.pdf](main.pdf). Everything except the comparison results is
written from the **current code** (`backend/`, `frontend/`) and the measured results in `TESTING.md` / `docs/`.

| Colour / mark in the PDF | Meaning | What you do |
|---|---|---|
| **Red** text, figures stamped **MOCK DATA** | Placeholder comparison numbers and discussion | Run the experiments below, then replace them |
| **Blue `[brackets]`** | Facts only your team can supply (training run, dataset, emails) | Fill them in |
| Black | Taken from the code or from measured results | Leave as is (re-check if code changes) |

Before submission: delete the `\thanks{DRAFT ...}` line in `main.tex` and make `\mock` / `\tbd` print in black
(or remove them).

---

## 0. Fill in the blue placeholders first (no experiments needed)

1. **Training details for Module 1 (Section IV-A).** The repo has no training script, only the weights
   (`best_resnet50_coffee.pth`). Take these from your actual training notebook: dataset source(s), images per class,
   train/val/test split, optimiser, learning rate and schedule, epochs, batch size, loss weighting, augmentations.
   ⚠️ The old documents disagree with each other, so do **not** copy them:
   - Phase-2 ESA PPT: ~10,000 images, 80/20 split, 15 epochs, rotation/flip/zoom/brightness.
   - Phase-2 ESA report: composite JMuBEN + PlantVillage + PlantDoc, 30 epochs, dropout 0.3, 89.4 % test accuracy.
   - `og/docs` and `docs/modules/module-1-cnn.md`: AdamW, cosine schedule, 96.4 % top-1, and a 5-model comparison table.
   - The deployed model has **dropout 0.4** (from the code), which already contradicts the report's 0.3.
   None of these numbers is backed by a script or log in the repo, so the paper does not use them.
2. **Emails** for all four authors (title block).
3. **Acknowledgment**: add estates or people who provided field images, if any.

## 1. Build the shared evaluation data (needed by everything below)

| Asset | Size (suggested) | Notes |
|---|---|---|
| Leaf test split | the held-out split from your training run (never used for training) | 5 classes: Rust, Cercospora, Phoma, Miner, Healthy |
| Field set | 150–300 phone photos from Chikkamagaluru estates | Different phones, light and backgrounds. This is where models really differ |
| RAG question set | 20–30 questions per disease (100–150 total), half in Kannada | For each question, mark which of the 931 chunks are relevant (2 annotators; agreement on a sample) |
| Chat question set | 100–150 questions: weather, dose, timing, organic, follow-ups with photos | Mix of English and Kannada |
| Speech set | 50–100 recorded utterances per language (Kannada, Indian English) with reference transcripts | Record in the field if possible (noise) |

Keep all of these in a new folder, e.g. `IEEE-Paper/eval/`, with a README describing how each was collected.

## 2. Module 1 (CNN): compare against the papers' techniques

Papers: **Anudeep K.S. et al. (Grenze 2024)**, GoogLeNet transfer learning, and **Selva Kumar et al. (ICETCS 2024)**,
YOLOv8.

1. **Re-implement the baselines on YOUR training split** (published numbers come from different data and classes, so
   they can't be compared directly):
   - GoogLeNet: `torchvision.models.googlenet(weights="IMAGENET1K_V1")`, replace `fc` with 5 outputs, fine-tune the
     last layers (they fine-tuned the last three), Adam + cross-entropy, 30 epochs, 80/20 split, as in their paper.
   - YOLOv8: the paper uses instance segmentation, which needs polygon labels you probably don't have. Use
     **YOLOv8-cls** (`ultralytics`, `yolov8s-cls.pt`) as the classification equivalent, and say so in the paper.
2. **Evaluate all three** (PlantIQ ResNet-50 with the existing weights, GoogLeNet, YOLOv8-cls) on the same test split
   **and** on the field set: accuracy, macro precision/recall/F1, per-class F1, confusion matrix, parameters and CPU
   latency (batch 1, median of 100 runs). Use `sklearn.metrics.classification_report` and `confusion_matrix`.
3. Optional and strong: a calibration check (expected calibration error) and how many wrong predictions the 75 %
   confidence gate catches. This directly supports the "blended" contribution.
4. Paste the results into `scripts/mock_data.json` → `cnn_comparison`, `cnn_confusion` (set `"is_mock": false`), and
   into **Table VII** in `main.tex`. Rewrite the red paragraph in Section IX-B.

## 3. Module 2 (RAG + environment): compare against the papers' techniques

Papers: **Selva Kumar et al.** (dense vector store + GPT-3.5 via LangChain), and the evaluation method of
**Farmer.Chat** (RAGAS context precision, faithfulness, relevance). Zhao et al. (knowledge graph) stays in Related
Work only. Re-implementing it is out of scope.

1. **Retrieval ablation** (Fig. 6). Write a script that calls `HybridRetriever` with parts switched off:
   dense only → BM25 only → dense+BM25 (RRF) → + rerank → full (+ topic filter, MMR). Compute **Recall@3** and
   **nDCG@3** against your labelled relevant chunks. All the pieces already exist in
   `backend/app/services/rag/retriever.py`: `_dense`, `_sparse`, `rrf_fuse`, `_rerank`, `mmr_select`.
2. **Baseline A, "Selva Kumar-style" RAG**: dense-only retrieval (top-3) + one LLM call, no weather, no dose audit.
   Use GPT-3.5 if you have an OpenAI key; otherwise use the same Gemini model and say so (this isolates the effect of
   retrieval).
3. **Baseline B**: the same LLM with **no retrieval**.
4. **Score generation** with `ragas` (faithfulness, answer relevancy, context precision) and count **unsupported
   doses** with the existing `audit_dosages()` from `backend/app/services/rag/query.py` on every answer.
5. Record latency per system.
6. Environment: optional sanity check of the risk rule. Compare the daily risk level against estate disease
   observations if CCRI or a planter can share them. Otherwise leave it described as rule-based (already stated as a
   limitation).
7. Update `rag_ablation`, `generation_comparison` in `mock_data.json`, **Table VIII**, and the red text in IX-C.

## 4. Module 3 (Chatbot): compare against Farmer.Chat

Paper: **Singh et al., Farmer.Chat (arXiv:2409.08916)**. You cannot run Farmer.Chat itself, so compare against its
**reported numbers and metric definitions**, and make that explicit in the text. Their reported values are in the
PDF: ~75 % of queries answered, average context precision 71 %, high faithfulness for ~80 % of queries, 67 % highly
relevant, most latencies 7.5–12.5 s. Use their definitions exactly.

1. Run your chat question set through `/api/v1/chat` (with and without GPS, with photos).
2. Measure: **answered rate** (not "I don't know" / not off-topic), **faithfulness** and **relevance** (RAGAS),
   **median latency**, and **Kannada fluency** (1–5, rated by at least 3 native speakers, report mean ± sd).
3. **Speech**: word error rate (`jiwer`) for local IndicConformer / Svarah-Whisper vs Groq whisper-large-v3 on your
   recordings (Fig. 8).
4. Update `chatbot_comparison`, `stt_wer`, **Table IX**, and the red text in IX-D.
   Note: Table IX puts Farmer.Chat's numbers next to yours, so say in the caption that theirs are as reported.

## 5. Module 4 (Market discovery): no comparison

As agreed, M4 is not compared. The paper describes it and reports its test coverage plus the 500-listing
performance test. Nothing to run unless you want a larger load test, e.g. distance sort latency at 1k/5k/10k listings.

## 6. References: please review

`references.bib` has two groups.

**Group A, your papers** (details taken from the PDFs in `Old-Documents/Research Papers`):

| Key | Check |
|---|---|
| `selvakumar2024rag` | DOI 10.1109/ICETCS61022.2024.10543859. Add page numbers from IEEE Xplore |
| `anudeep2024cnn` | Grenze ID 01.GIJET.10.2.571_2. Add pages from the journal site (the PDF shows page 1319) |
| `sapkota2024mmllm` | **The PDF shows no venue.** Your PPT says IEEE Trans. Automation Science and Engineering. Confirm and fill in, or cite as arXiv with its ID |
| `singh2024farmerchat` | arXiv:2409.08916 (from the PDF). Check whether it has since been published |
| `zhao2024kg`, `santhosha2023yield`, `patil2022elevation`, `xavier2023price` | Complete as given in the PDFs. Add page numbers for Xavier from IEEE Xplore |
| `he2016resnet`, `lewis2020rag` | From your Phase-2 reference list |
| `reimers2019sbert` | In your old reference list but **not cited** in the paper (the current code uses bge-m3, not SBERT). Not printed |

**Group B, added by me for techniques the code actually uses. Please review and accept or reject each:**

| Key | Supports | Confidence |
|---|---|---|
| `deng2009imagenet` | ImageNet pre-training | High |
| `robertson2009bm25` | BM25 | High |
| `cormack2009rrf` | Reciprocal rank fusion | High |
| `carbonell1998mmr` | MMR | High |
| `chen2024bgem3` | bge-m3 embedder (arXiv:2402.03216) | High. Check author list |
| `johnson2021faiss` | FAISS | High. Check vol/pages |
| `nogueira2019rerank` | Cross-encoder reranking | High |
| `radford2023whisper` | Whisper | High. Check pages |
| `es2023ragas` | RAGAS metrics (arXiv:2309.15217) | High |
| `sinnott1984haversine` | Haversine formula | High |
| `biryukov2016argon2` | Argon2 | High. Check pages |

**Further references you could add** (not in the paper yet; verify before using):
- Esgario, Krohling & Ventura, "Deep learning for classification and severity estimation of coffee leaf biotic
  stress", *Computers and Electronics in Agriculture*, 2020 (BRACOL coffee dataset). A strong extra Module 1 baseline
  or dataset.
- Jepkoech et al., "Arabica coffee leaf images dataset for coffee leaf disease detection and classification",
  *Data in Brief*, 2021 (JMuBEN). Cite only if your training data actually used it.
- Mohanty, Hughes & Salathé, "Using deep learning for image-based plant disease detection", *Frontiers in Plant
  Science*, 2016. Classic plant-disease CNN reference.
- Avelino et al., "The coffee rust crises in Colombia and Central America (2008–2013)", *Food Security*, 2015.
  Motivation for rust and weather.
- Guo et al., "On calibration of modern neural networks", ICML 2017. Needed if you add calibration (temperature
  scaling) to Module 1.
- Javed et al., "Svarah: Evaluating English ASR systems on Indian accents", Interspeech 2023. For the English STT model.
- AI4Bharat IndicConformer / IndicVoices paper. For the Kannada STT model (find the exact citation on the model card).
- Gemini 2.5 technical report and the gpt-oss model card. If the reviewers want the LLMs cited.

## 7. Regenerate figures and the PDF

```bash
# from IEEE-Paper/ (needs Python with matplotlib)
python scripts/make_figures.py
```

```bash
# compile (Tectonic is in tools/; or upload the folder to Overleaf)
tools/tectonic.exe main.tex
```

`tools/` is git-ignored. On Overleaf, upload `main.tex`, `references.bib`, `IEEEtran.cls` and `figures/`.

## 8. Final checklist before submission
- [ ] Every red value replaced by a real result; every "MOCK DATA" figure regenerated with `is_mock: false`
- [ ] Every blue `[...]` filled in
- [ ] `\thanks{DRAFT...}` removed; `\mock` / `\tbd` made black
- [ ] Abstract's last sentence rewritten with the real headline result
- [ ] Group B references reviewed
- [ ] Page limit of the target conference checked (currently 10 pages; most IEEE conferences allow 6–8, so the
      Implementation/Testing tables and Algorithm 1 are the first to cut)
- [ ] Re-check numbers in Sections III–VII if the code changed after 2026-11-13
