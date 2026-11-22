# PlantIQ comparison study: how to run it

Everything for the paper's missing comparison numbers lives in this folder. The PlantIQ app is never imported or
changed. The *why* is in [PLAN.md](PLAN.md); this file is the *how*.

```
compare/
  00_env/            00_gpu_check.ipynb                  GPU + package check
  01_dataset_audit/  01_dataset_audit.ipynb              duplicates, leak-free 5-fold split (outputs/)
  02_cnn/            02a … 02h                           CNN training, benchmark, export (runs/ = checkpoints)
  03_rag/            03a … 03d, plantiq_rag_snapshot/   RAG question set, benchmarks, report
  04_export/         04_paper_numbers.ipynb              everything → results/paper_numbers.json
  05_chat/           05a, 05b, plantiq_chat_snapshot/   chatbot (Module 3) test conversations, prompts, report
  common/            shared Python code (data, training loop, metrics, LLM client, RAG scoring)
  results/           every number (JSON/CSV), figures/, RESULTS.md
```

---

## 1. One-time setup (≈10 min)

You need: Windows, the NVIDIA driver you already have (610.62, nothing to install), Python 3.11
(`C:\Users\...\Python311`), about 8 GB free on D: (environment ≈ 6 GB, checkpoints ≈ 2 GB) and about 5 GB free on
C: (the RAG models, downloaded once into `C:\Users\<you>\.cache\huggingface`).

The environment `compare/.venv` has **already been created and tested on this machine**. Run these only if you
need to rebuild it (e.g. on another computer). Run them from the `compare` folder, in a terminal (PowerShell or
Antigravity's terminal):

```bash
python -m venv .venv
```

```bash
.venv\Scripts\python -m pip install --upgrade pip
```

```bash
.venv\Scripts\python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

```bash
.venv\Scripts\python -m pip install -r requirements.txt
```

```bash
.venv\Scripts\python -m ipykernel install --user --name plantiq-compare --display-name "PlantIQ compare (GPU)"
```

Check the GPU is visible (must print `True` and your RTX 3070):

```bash
.venv\Scripts\python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

### Antigravity IDE
1. **File → Open Folder…** → `D:\plantiq-capstone\compare` (open this folder, not the repo root).
2. Install the **Jupyter** and **Python** extensions if they aren't installed yet (Extensions panel, by
   Microsoft/ms-toolsai).
3. Open a notebook, click **Select Kernel** (top right) → *Jupyter Kernel* → **PlantIQ compare (GPU)**.
   If it's not listed: *Python Environments…* → `compare\.venv\Scripts\python.exe`.
4. Run a notebook with **Run All**. Keep the laptop **plugged in** and Windows on **Best performance**, otherwise
   the GPU slows down a lot.
5. Run notebooks **one at a time** (they share the GPU). Close a finished notebook or restart its kernel before
   starting the next, to free GPU memory.

### RAG part: no API key needed
The RAG benchmark tests the **retrieval-augmented pipelines, not the language model**, and runs without any API:

* `03a` freezes the fixed question set (`03_rag/questions_curated.json`, built by `03_rag/make_questions.py`):
  54 English questions on Karnataka coffee disease, pests and cultivation, plus 21 Kannada versions; every gold
  evidence quote is verified word-for-word against the PDF text.
* `03b` runs both retrievers (PlantIQ hybrid and the Selva Kumar et al. LangChain dense retriever) on all questions,
  locally on the GPU.
* `03c` builds the exact prompt each system would send to its LLM and writes them all to
  `03_rag/answers/generation_inputs.jsonl`.
* Answers and scores: one model answers every prompt in that file (so only the RAG differs) and every answer is scored
  against the gold answer and the retrieved passages. They are stored in `03_rag/answers/answers.jsonl` and
  `03_rag/answers/judgments.jsonl`, with the model named in each record.
* `03d` computes the results and figures; the rule-based dose audit and the retrieval metrics are an independent
  cross-check that needs no judge.

The `.env` / Gemini settings are only needed if you want an LLM to answer the prompts automatically instead.

---

## 2. Run order

| # | Notebook | What it does | Time* | Needs |
|---|---|---|---|---|
| 0 | `00_env/00_gpu_check` | GPU, packages, dataset, weights present | 1 min | – |
| 1 | `01_dataset_audit/01_dataset_audit` | duplicates, leak check, the 5-fold split everyone uses | 5 min | 0 |
| 2 | `02_cnn/02a_resnet50_current_recipe` | **R0**: current recipe on clean folds | ≈ 50 min | 1 |
| 3 | `02_cnn/02b_resnet50_v2_ablation` | choose the improvements for **V2** (fold 0) | ≈ 40 min | 2 |
| 4 | `02_cnn/02c_resnet50_v2_cv` | **V2** on all folds | ≈ 35 min | 3 |
| 5 | `02_cnn/02d_googlenet_anudeep` | **G1** baseline | ≈ 15 min | 1 |
| 6 | `02_cnn/02e_yolov8cls_selvakumar` | **Y1** baseline | ≈ 40 min | 1 |
| 7 | `02_cnn/02f_deployed_weights_eval` | **D0** current backend weights | 2 min | 1 |
| 8 | `02_cnn/02g_cnn_benchmark` | all CNN metrics, tests, figures, **replace/keep decision** | 2 min | 2-7 |
| 9 | `02_cnn/02h_export_final_model` | only if 8 says REPLACE: final V2 weights in backend format | 10 min | 8 |
| 10 | `03_rag/03a_build_question_set` | freeze the 54 + 21 verified questions | 1 min | – |
| 11 | `03_rag/03b_retrieval_benchmark` | retrieval ablation + Selva Kumar retriever (first run downloads ~4.5 GB of models) | 10-20 min | 10 |
| 12 | `03_rag/03c_generation_benchmark` | exact prompts of the 3 systems → `answers/generation_inputs.jsonl`; then answers + judgments are added | 5 min | 10 |
| 13 | `03_rag/03d_rag_report` | RAG tables and figures (generation part once answers/judgments exist) | 1 min | 11, 12 |
| 14 | `04_export/04_paper_numbers` | `results/paper_numbers.json` + `results/RESULTS.md` | 1 min | 8, 13 |
| 15 | `05_chat/05a_build_chat_prompts` | 43 chat conversations → exact prompts of PlantIQ, the LangChain Selva Kumar chatbot and PlantIQ offline (`05_chat/answers/chat_inputs.jsonl`); re-run once per turn depth after its answers are added (`05_chat/add.py`) | 2 min | 11 |
| 16 | `05_chat/05b_chat_report` | Module 3 scores → `results/chat/chat.json`, `chat_rows.csv`, `figures/fig_chat.png` | 1 min | 15 |

\*RTX 3070 Laptop estimates; the GPU part (2-7) is about 3-3.5 h in total and can run unattended. Every training
notebook **resumes**: if you stop it, finished folds are skipped on the next run. To redo a fold, delete
`02_cnn/runs/<MODEL>/fold<k>/`.

The CNN track (2-9) and the RAG question set (10) can overlap: start the GPU notebooks, and build the questions
while they train.

Want it faster? Put the line `PLANTIQ_FOLDS=3` in `compare/.env` **before** running notebook 1 (it then makes 3
folds; all later notebooks follow). Wider confidence intervals, about 40% less time. Don't change it after
notebook 1 has run, or the split and the trained folds no longer match.

---

## 3. When to show me the results

Send me a message at these three checkpoints (just say "checkpoint N done"; I read the files directly):

1. **After notebook 1 (dataset audit).** I check `01_dataset_audit/outputs/audit_report.md` and the fold summary
   before any GPU time is spent.
2. **After notebook 8 (CNN benchmark).** I check `results/RESULTS_cnn.md`, `results/cnn/decision.json` and the
   figures, and we decide whether to run 02h and replace the model.
3. **After notebook 13 (RAG report),** or earlier if 03a's questions look wrong to you (they are in
   `03_rag/data/questions_review.csv`; set `status` to `reject` or `edit` a row and re-run 03a to apply).

If any notebook stops with an error, send me the notebook name and the last cell's error text.

---

## 4. What each result file is

| File | Content |
|---|---|
| `01_dataset_audit/outputs/audit_report.md` | duplicate table, leak rate of a random split, fold summary |
| `01_dataset_audit/outputs/splits.csv` (+ `.sha256`) | the frozen split; every model's result records this hash |
| `results/cnn/preds/<MODEL>_fold<k>_{val,test}.csv` | per-image logits for every model and fold |
| `results/cnn/<MODEL>_summary.json`, `<MODEL>_cost.json` | training log summary; params, GFLOPs, latency |
| `results/cnn/v2_ablation.json`, `v2_config.json` | ablation steps and the chosen V2 recipe |
| `results/cnn/benchmark.json`, `decision.json` | all CNN metrics with CIs and paired tests; the replacement decision |
| `results/rag/retrieval.json`, `generation.json` (+ row-level CSV/JSONL) | RAG metrics with CIs |
| `results/figures/*.png|pdf` | figures for the paper (same file names as `IEEE-Paper/figures/`) |
| `results/paper_numbers.json` | all paper numbers, same layout as `IEEE-Paper/scripts/mock_data.json` |
| `results/RESULTS.md` | human-readable summary of everything |

## 5. Troubleshooting

| Problem | Fix |
|---|---|
| `PyTorch cannot see the GPU` | Kernel is wrong: pick **PlantIQ compare (GPU)**. Check with the command in §1. |
| CUDA out of memory | Another notebook's kernel still holds GPU memory. In each finished notebook click **Restart** (or close it and shut its kernel down), close Steam and GPU-heavy browser tabs, check with `nvidia-smi` that less than 1 GB is used, then re-run. Finished folds are kept. |
| `Couldn't open shared file mapping … error code: <1455>` | Windows ran out of memory (RAM + page file). Restart the kernel, close Brave/Steam and other notebooks, re-run; finished steps/folds are kept. If it repeats, set `workers=2` in that notebook's config. |
| Training is slow (< 200 img/s in the log) | Plug in the laptop, Windows power mode **Best performance**, close games/browsers using the GPU. |
| `predictions missing` in 02g | That model's notebook hasn't finished all folds yet. |
| `…_API_KEY is not set` | Fill `.env` (see `.env.example`), or point that role to a provider you have a key for. |
| HTTP 429 (rate limit) | Set e.g. `GEMINI_RPM=8` in `.env` and re-run; cached answers are not requested again. |

## 6. Self-test (what I ran before handing this over)

`PLANTIQ_SMOKE=1` runs every notebook end to end on a tiny subset (1 epoch, a few images, fake LLM) and writes
only into `_smoke/` (git-ignored), so it can never mix with real results. All 15 notebooks passed this test on
this machine (RTX 3070 Ti Laptop), and the test outputs were then deleted, so every number you produce comes from
your own run. Measured here: ResNet-50 training ≈ 400 images/s, data loading ≈ 870 images/s (6 workers).
`_cache/` keeps the decoded images and the YOLOv8 weights so your first run starts faster.
