# PlantIQ comparison study: plan

Goal: replace every red/"MOCK" number in `IEEE-Paper/main.tex` (Tables VII and VIII, Figs. on CNN comparison,
confusion matrix, RAG ablation and generation) with real, reproducible measurements. Everything lives in `compare/`.
The PlantIQ app (`backend/`, `frontend/`) is **not** imported or changed. Where we need PlantIQ's RAG logic we copy a
frozen snapshot into `compare/` and record the commit it came from.

Scope: Module 1 (CNN) and Module 2 (RAG). Module 3 (chatbot / speech) is out of scope for now.

---

## 0. What we found before planning

### 0.1 The dataset (JMuBEN, `dataset-coffee-leaves-images/Original`)

Numbers from `01_dataset_audit/outputs/audit_report.md`. A random file split puts a copy of **100%** of test files into training.

| Class | Files | Byte-unique files (MD5) | Distinct patches, perceptual hash | Distinct patches, pixel check (strict) |
|---|---:|---:|---:|---:|
| Cerscospora | 7,681 | 322 | 82 | 79 |
| Healthy | 18,983 | **62** | **14** | **9** |
| Leaf rust | 8,336 | 1,042 | 519 | 277 |
| Miner | 16,978 | 1,639 | 410 | 316 |
| Phoma | 6,571 | 691 | 181 | 180 |
| **Total** | **58,549** | **3,756** | **1,206** | **861** |

- 94% of the files are exact byte copies (same MD5). The rest are rotated / flipped / colour-shifted copies of the
  same 128x128 leaf patch: for over 90% of the byte-unique images, a rotation or flip of another image matches it
  pixel for pixel. In practice the dataset has roughly **860-1,200 different leaf patches**, not 58,000.
  Perceptual hash = rotation/flip-invariant pHash; pixel check = mean absolute pixel difference < 6/255 under any
  rotation/flip. For splitting we use the **strict** grouping (merging both), because over-merging only costs a
  little data while under-merging leaks test images into training.
- No group spans two classes, so labels are consistent.
- 95% of images are 128x128 crops of a leaf, not whole-leaf photos.
- **Consequence:** the old notebook (`cnn-ipynb/model_latest.ipynb`) split files at random, so copies of the same
  patch landed in train, val and test. Its "100% validation accuracy" is leakage, not real performance. Any number
  produced that way cannot go in the paper.
- **Healthy is the weak spot:** ~19k files but only about 9-12 distinct patches. Any score on Healthy rests on very
  few real examples. We handle this with cross-validation (every patch is tested exactly once) and say it plainly in
  the paper.

### 0.2 The deployed model is not the notebook model

`backend/data/models/best_resnet50_coffee.pth` uses a `Dropout(0.4) + Linear` head, 224x224 input and class order
`[Miner, Rust, Phoma, Healthy, Cerscospora]`. The notebook trains a plain `Linear` head at 128x128 with alphabetical
class order. So the deployed weights come from a different, unrecorded run, most likely on a random split of this same
dataset. That means **the deployed weights have probably seen almost every patch**, so testing them on this dataset is
not a fair score. We still report them, clearly marked, and score them fairly on an external set (if we get one, §2.7).

### 0.3 Your machine

- GPU: NVIDIA GeForce RTX 3070 Laptop, 8 GB, driver 610.62 (supports CUDA 13.x). **No driver install needed.**
- Python 3.11 is installed. There is no PyTorch environment yet; we create one in `compare/.venv` with the CUDA
  build of PyTorch (§1).

### 0.4 What the baseline papers actually did

| Paper | Model | Recipe stated in the paper | What we can reproduce |
|---|---|---|---|
| Anudeep K.S. et al. (Grenze 2024) | GoogLeNet transfer learning | 224x224, fine-tune last three layers, softmax classifier, 30 epochs, 80/20 split | Exactly this, on our folds. Optimiser/LR not stated: Adam, lr 1e-3 (stated as our choice) |
| Selva Kumar et al. (ICETCS 2024) | YOLOv8 instance segmentation + EasyOCR label read-out | flip, rotation, brightness augmentation; RAG: PDFs, chunks, OpenAI embeddings, vector store, LangChain conversational chain, GPT-3.5 | Segmentation needs polygon masks we don't have, so **YOLOv8-cls** (same backbone family, classification head). For RAG: their pipeline as described |

---

## 1. Folder layout and environment

```
compare/
  PLAN.md                         this file
  README.md                       how to run everything, in order
  requirements.txt                pinned versions
  .venv/                          git-ignored
  dataset-coffee-leaves-images/   raw data, read-only, never modified
  cnn-ipynb/                      the old notebook, read-only reference
  common/                         small shared Python helpers (data loading, metrics, latency). See note below
  00_env/
    00_gpu_check.ipynb            fails loudly if CUDA is not used
  01_dataset_audit/
    01_dataset_audit.ipynb        hashes, duplicate groups, figures, split manifests
    outputs/                      audit_report.md, files.csv, groups.csv, folds.csv (+ SHA-256)
  02_cnn/
    02a_resnet50_current_recipe.ipynb   R0: the old notebook's recipe, retrained on the clean folds
    02b_resnet50_v2_ablation.ipynb      try the improvements on fold 0, pick the best set
    02c_resnet50_v2_cv.ipynb            the chosen v2 recipe on all 5 folds
    02d_googlenet_anudeep.ipynb         baseline 1
    02e_yolov8cls_selvakumar.ipynb      baseline 2
    02f_deployed_weights_eval.ipynb     the current backend weights, as-is (marked as contaminated)
    02g_cnn_benchmark.ipynb             all metrics, tests, tables, figures
    02h_export_final_model.ipynb        only if v2 wins: train on all data, export in backend format
    runs/                         checkpoints + per-run logs (git-ignored, large)
  03_rag/
    kb/                           copy of the 14 knowledge-base PDFs (+ SHA manifest)
    plantiq_rag_snapshot/         frozen copy of backend/app/services/rag at commit 560e9af
    03a_build_question_set.ipynb
    03b_retrieval_benchmark.ipynb
    03c_generation_benchmark.ipynb
    03d_rag_report.ipynb
    data/                         questions.jsonl (frozen, with SHA-256)
  results/
    cnn/*.json, rag/*.json        one file per run, never overwritten
    paper_numbers.json            same schema as IEEE-Paper/scripts/mock_data.json, is_mock=false
    figures/                      PNG + PDF for the paper
    RESULTS.md                    human-readable summary with every number traced to its run
```

Note on `common/`: training happens in notebooks, as you asked. A few helpers (dataset class, metric functions,
latency timer) sit in `common/*.py` for two reasons: (1) every model is scored by the *same* code, which is what makes
the comparison fair, and (2) on Windows, PyTorch data-loader workers cannot use functions defined inside a notebook.

**Environment (step E1):**
- `python -m venv compare/.venv`, then PyTorch + torchvision from the official CUDA 12.8 wheel index, plus
  `ultralytics`, `scikit-learn`, `pandas`, `matplotlib`, `seaborn`, `imagehash`, `jupyter`, `ipykernel`, `papermill`.
- Register the kernel as **"PlantIQ compare (GPU)"**.
- Add to `.gitignore`: `compare/.venv/`, `compare/.env`, `compare/02_cnn/runs/`, and the 1.9 GB `compare/dataset-coffee-leaves-images/` (the audit stores file hashes instead, so the exact dataset can be verified).
- `00_gpu_check.ipynb` asserts `torch.cuda.is_available()`, prints the GPU name, runs a timed matmul on GPU vs CPU.
  Every training notebook starts with the same assert, so nothing can silently fall back to CPU.
- Speed settings used everywhere: mixed precision (AMP) and `cudnn.benchmark=True` (`channels_last` was tested and is 9x slower on this GPU/driver, so it is not used), and the (small)
  de-duplicated image set preloaded into RAM with augmentation on the GPU. That avoids slow disk reads and Windows
  worker issues.
- Laptop note: keep it plugged in and on the "Best performance" power mode while training.

I run the notebooks for you with papermill, so the outputs are saved inside each `.ipynb`; you can also open and run
any of them yourself in VS Code / Jupyter.

---

## 2. Module 1: CNN benchmark

### 2.1 Clean data and splits (`01_dataset_audit.ipynb`)

1. Hash every file: MD5 (exact copies) and a rotation/flip-invariant perceptual hash, checked by pixel difference.
2. Give every file a **`source_id`** (the patch it was copied from).
3. Training pool = one file per MD5 (byte copies add nothing). The rotated/flipped/colour copies stay, because they are
   real pixel variation; and we augment online anyway.
4. Split with **StratifiedGroupKFold (k=5, seed 42)** on `source_id`: a patch and all its copies are always on the same
   side, and each fold keeps the class mix. Inside each training fold, 15% of groups are held out as validation (for
   early stopping and choosing settings). The test fold is never looked at until the final evaluation.
5. Save `folds.csv` (file, class, source_id, fold) and its SHA-256. **Every model uses exactly this file.**
6. Outputs for the paper: the table in §0.1, a group-size histogram and a sample grid of duplicates. This is itself a
   finding worth one paragraph in the paper (data leakage in JMuBEN under random splits).

Why 5-fold CV and not one 80/20 split: with ~860 patches (and 9 Healthy), a single test split would be small and
noisy. With 5 folds every patch is tested exactly once (out-of-fold predictions), so results use the whole dataset.

### 2.2 Models (all trained on the same 5 folds)

| ID | Model | Recipe |
|---|---|---|
| R0 | ResNet-50, **current recipe** | Copied from `model_latest.ipynb`: 128 px, AutoAugment, AdamW lr 3e-4, wd 1e-4, cosine, 15 epochs, batch 32 |
| V2 | ResNet-50, **improved** | Chosen in §2.3 |
| G1 | GoogLeNet (Anudeep K.S. et al.) | 224 px, ImageNet weights, last three layers trainable, Adam, cross-entropy, 30 epochs; same 150k-sample budget as V2 |
| Y1 | YOLOv8s-cls (Selva Kumar et al.) | `yolov8s-cls.pt`, flips + brightness augmentation as in the paper, 60 epochs over the byte-unique training images (~150k samples, same budget as V2) |
| D0 | Deployed backend weights | No training. Scored as-is, labelled "trained on unknown split, likely contaminated" |

### 2.3 Making ResNet-50 better (V2)

Candidate changes, each tested on fold 0 against R0 using **validation macro-F1** (never the test fold):

1. Input 224 px (upsampled from 128) instead of 128: ResNet-50's ImageNet features fit 224.
2. Class-balanced sampling (each class equally likely per batch; each patch equally likely within its class), so
   Healthy's thousands of copies don't dominate.
3. Augmentation matched to leaf patches: all 8 rotations/flips, random resized crop (0.6-1.0), colour jitter, random
   erasing; plus MixUp/CutMix as a separate trial.
4. Optimisation: AdamW with lower LR for the backbone than the head, 1-epoch warm-up + cosine, label smoothing 0.1,
   weight EMA, early stopping on val macro-F1.
5. Head: `Dropout(0.4) + Linear(2048, 5)` and class order `[Miner, Rust, Phoma, Healthy, Cerscospora]`, identical to
   the backend, so the final weights are a drop-in replacement.
6. After training: temperature scaling on the validation set, so the probabilities are calibrated. This matters
   because the app uses a 75% confidence gate.
7. Optional: 8-way test-time augmentation; reported separately because it costs 8x latency.

We add changes in steps (ablation table: R0 → +224 → +balanced → +aug → +optim → +TS) and keep only what helps. That
ablation table is also paper material.

### 2.4 Benchmark: exactly what is measured

All computed by the same code in `common/metrics.py` from saved per-image predictions.

| Metric | Definition |
|---|---|
| Accuracy | Out-of-fold, over all test images |
| **Macro-F1 (primary)** | Unweighted mean of per-class F1, so Healthy counts as much as Miner |
| Macro precision / recall, per-class F1 | sklearn `classification_report` |
| Balanced accuracy | Mean per-class recall |
| Confusion matrix | Out-of-fold, row-normalised |
| Fold spread | Mean ± std of macro-F1 over the 5 folds |
| 95% CI | **Group bootstrap** (resample source patches, not files, 2,000 times), so copies don't fake confidence |
| Calibration | Expected Calibration Error (15 bins), before and after temperature scaling |
| Confidence gate | At threshold 0.75: coverage (% answered) and accuracy on answered, plus % of errors caught |
| Size | Parameters, file size (MB), GFLOPs at the model's input size |
| Latency | Batch 1, 20 warm-up + 200 timed runs, median and p95, on GPU (RTX 3070 Laptop) and CPU |
| Training cost | Wall-clock minutes per fold on the same GPU |

Significance: V2 vs each other model with a **paired group-bootstrap of the macro-F1 difference** and **McNemar's test**
on the out-of-fold predictions.

### 2.5 Replacement rule (decided before we see the results)

V2 replaces the current model only if **all** hold:
1. Out-of-fold macro-F1 of V2 > R0, and the 95% CI of the difference is above 0 (or McNemar p < 0.05).
2. No class's F1 drops by more than 2 points.
3. Calibrated ECE is not worse than R0's.
4. CPU latency is at most 1.25x the current model's (54.9 ms).

If V2 wins: `02h` retrains V2 on all data with the same recipe and epoch count, exports
`best_resnet50_coffee_v2.pth` in the backend format plus its SHA-256 and the temperature value. Swapping it into the
backend is a separate step that you approve later.

### 2.6 Time estimate on your GPU

De-duplicated, the training set is small, so runs are short. Estimates (RTX 3070 Laptop, AMP):

| Work | Runs | Approx. time |
|---|---|---|
| Dataset audit + folds | 1 | 5 min |
| R0, 5 folds | 5 | 30-40 min |
| V2 ablation on fold 0 | ~6 | 60-80 min |
| V2, 5 folds | 5 | 50-60 min |
| GoogLeNet, 5 folds | 5 | 15 min |
| YOLOv8-cls, 5 folds | 5 | 30-40 min |
| Benchmark + figures | 1 | 15 min |
| **Total** | | **about 3-3.5 h of GPU time** (measured throughput on this laptop), unattended |

To save time we can drop to 3 folds (about 3 h); the cost is wider confidence intervals.

### 2.7 External test set (recommended)

All JMuBEN numbers measure in-dataset performance. Reviewers will ask how the models do on other images. Options:
(a) 150-300 of your own field photos from Chikkamagaluru (best, the paper already promises a field set), or
(b) a public coffee-leaf dataset with the same classes (e.g. BRACOL, Esgario et al. 2020: rust, miner, phoma,
cercospora, healthy), cut into leaf patches. **No model is trained on it**; it is only for testing all five models
(including D0, which can only be scored fairly here).

### 2.8 Paper outputs (Module 1)
Table VII (real), Fig. CNN comparison, Fig. confusion matrix (V2, out-of-fold), new small table: V2 ablation, new
paragraph: dataset duplication and why group-aware splits are needed. The blue `[training details]` placeholders in
Section IV-A get filled with V2's actual recipe.

---

## 3. Module 2: RAG benchmark

### 3.1 Knowledge base
Copy the 14 PDFs from `backend/data/knowledge_base` into `compare/03_rag/kb/` with a SHA-256 manifest. Every system
uses exactly these PDFs.

### 3.2 Question set (`03a_build_question_set.ipynb`): the measurable part
1. Topics: rust, Cercospora, Phoma, leaf miner, general/nutrition. **30 questions each = 150.**
2. For each question we store: the question, a short **gold answer**, and one or more **gold evidence quotes**: exact
   sentences copied from a KB PDF (file + page). Making relevance a quote, not a chunk ID, means every system can be
   scored the same way regardless of how it chunks the PDFs.
3. How they are made: an LLM drafts questions from randomly sampled KB passages (the passage gives the evidence
   quote); the team accepts, edits or rejects each one; at least 30 questions are written by the team from scratch so
   the set isn't only LLM-shaped. Questions whose answer is not in the KB (10 extra) test whether a system admits it
   doesn't know.
4. Half the questions get a Kannada version (LLM translation, checked by a native speaker on the team).
5. Freeze as `questions.jsonl` with SHA-256. Nothing is tuned after freezing.

### 3.3 Systems

| ID | System | Details |
|---|---|---|
| L0 | LLM, no retrieval | Same LLM and prompt as PlantIQ, no context |
| SK | Selva Kumar et al. style RAG | LangChain, PyPDF loader, `RecursiveCharacterTextSplitter` (1000/200), OpenAI embeddings, FAISS, top-4, `ConversationalRetrievalChain`, GPT-3.5-turbo |
| SK-g | SK retrieval + PlantIQ's LLM | Isolates retrieval quality from the LLM choice |
| PQ | PlantIQ hybrid RAG | Frozen snapshot: bge-m3 dense + BM25, RRF, bge-reranker, topic filter, MMR, same prompt, dose audit |

Retrieval ablation inside PQ (for the existing ablation figure): dense only → BM25 only → dense+BM25 (RRF) → + rerank →
full (+ topic filter + MMR). Same LLM throughout.

### 3.4 Benchmark: exactly what is measured

| Metric | Definition |
|---|---|
| Recall@3, Recall@5 | Share of a question's gold quotes found in the top-k chunks (a chunk "contains" a quote if ≥ 80% of the quote's tokens appear in order, fuzzy match) |
| nDCG@3, MRR@10, Hit@1 | Standard ranking metrics with the same relevance rule |
| Faithfulness | RAGAS: share of answer claims supported by the retrieved context |
| Answer relevancy | RAGAS |
| Context precision | RAGAS, using the gold answer |
| Answer correctness | RAGAS, against the gold answer |
| Unsupported doses | % of answers containing a dose/rate not found in the retrieved context (same audit logic as PlantIQ, applied to every system) |
| Abstention | On the 10 out-of-KB questions: % where the system says it doesn't know |
| Latency | Median and p95 end-to-end seconds per question |

All metrics are reported overall and split by English / Kannada. RAGAS uses one fixed judge model at temperature 0
for every system, preferably a different model from the generators. Two team members check 30 judged answers by hand
and we report agreement with the judge. CIs by bootstrap over questions; paired comparisons by Wilcoxon signed-rank.

### 3.5 Paper outputs (Module 2)
Table VIII (real), retrieval ablation figure, generation comparison figure, rewritten Section IX-C.

---

## 4. Reproducibility rules (apply to everything)
- Fixed seeds; seed, git commit, library versions, GPU name and folds SHA are written into every result JSON.
- One result file per run in `results/`, never overwritten; `RESULTS.md` traces every paper number to its file.
- Test folds and the frozen question set are only used for final scoring, never for choosing settings.
- The final notebook writes `results/paper_numbers.json` in the same format as `IEEE-Paper/scripts/mock_data.json`.
  Copying it into the paper and regenerating the figures/PDF is a separate step you approve.

## 5. Order of work and checkpoints

| Step | Output | You check |
|---|---|---|
| E1 Environment + GPU check | `.venv`, `00_gpu_check.ipynb` | GPU is used |
| D1 Dataset audit + folds | `folds.csv`, audit report | the duplicate findings |
| C1 R0 on 5 folds | baseline numbers | |
| C2 V2 ablation, then V2 on 5 folds | ablation table | which changes were kept |
| C3 GoogLeNet, YOLOv8-cls, deployed weights | | |
| C4 CNN benchmark | Table VII, figures, replace/keep decision | the decision |
| R1 Question set draft | `questions.jsonl` draft | **team reviews questions (manual work)** |
| R2 Retrieval + generation benchmarks | Table VIII, figures | |
| P1 Export to paper | `paper_numbers.json` | approve updating the paper |

CNN work (C1-C4) runs on the GPU while the team reviews the RAG question set, so the two tracks overlap.

## 6. What I need from you
1. **API keys** in `compare/.env` (git-ignored), for RAG only: an OpenAI key (for a faithful GPT-3.5 + OpenAI-embedding
   baseline and, ideally, the RAGAS judge), and the Gemini/Groq key PlantIQ uses. Without OpenAI we substitute and say
   so in the paper.
2. **External test set** for the CNN (§2.7): your own field photos, the public BRACOL set, or none.
3. **Time budget:** 5 folds (about 4-5 h GPU) or 3 folds (about 3 h).
4. Who on the team reviews the RAG questions and checks the Kannada translations.
