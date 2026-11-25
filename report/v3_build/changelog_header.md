## A. Formatting changes (whole document, following `report/Perfect.pdf`)

| # | Item | Original | Fixed copy |
|---|---|---|---|
| A1 | Document structure | PDF-to-Word conversion: 68 sections (one per page), text in floating frames, parts of sentences hidden behind text boxes | Clean Word document: 2 sections (front matter, body), real paragraphs, tables, equations and fields |
| A2 | Page size and margins | A4, uneven margins per page | A4; left 1.0 in, right 0.9 in, top 1.25 in, bottom 1.05 in on every page |
| A3 | Header (Chapter 1 onwards) | Title at 8 pt over two lines, logo, no rule | Title in Times New Roman 10 pt on the left, PES logo on the right, full-width rule underneath |
| A4 | Footer | `Aug – Nov 2026` and a bare number; Chapter 1 page printed two numbers | Rule above; `Dept. of CSE` left, `August - November, 2026` centre, `Page No.N` right, TNR 10 pt; numbering restarts at 1 on Chapter 1 |
| A5 | Front matter | Header/footer absent; mixed sizes | No header or footer, no page number (as in the reference) |
| A6 | Cover page | TNR 13 / 10 pt | Arial as in the reference: "Dissertation on" 16 pt bold italic, title 16 pt bold, degree lines 16 pt bold, names 12 pt bold, guide TNR 14 pt, department block 12 pt, address 10 pt |
| A7 | Certificate | TNR 9 to 13 pt | Arial: "CERTIFICATE" 20 pt bold, title 14 pt bold, body 10 pt justified, signatures 10 pt; fits on one page |
| A8 | Declaration | TNR 12 pt; no signature lines | Title TNR 18 pt bold; body TNR 14 pt justified with the title, degree and university in bold; SRN, name and signature line in 14 pt bold. Standard "We hereby declare" wording kept (your decision) |
| A9 | Acknowledgement | "We / us / our"; "Phase - 3" broken into a list item "3." | First person singular throughout ("I / me / my"); TNR 14 pt justified; list artefact removed |
| A10 | Abstract | Title 16 pt | Title TNR 18 pt bold; body TNR 12 pt, 1.5 spacing |
| A11 | Chapter openings | `CHAPTER N` centred with the title | `CHAPTER N` TNR 18 pt bold **left**; chapter title TNR 18 pt bold, centred, on its own line; every chapter starts on a new page |
| A12 | Headings | Mixed list-numbered and typed numbers; sentence case and Title Case mixed | Level 2 (`1.1`) TNR 16 pt bold, level 3 (`1.1.1`) TNR 14 pt bold, Title Case, numbers typed consistently |
| A13 | Body text | Justified, mixed spacing | TNR 12 pt, **left-aligned like the reference**, 1.5 line spacing, 8 pt after each paragraph; 18 pt / 12 pt before level-2 / level-3 headings |
| A14 | Lists | Mixed indents | Number or bullet at 0.25 in, text and wrapped lines at 0.5 in; bold label + colon where the item has a label |
| A15 | Captions | Bold 11 pt, some justified | TNR 10 pt, *italic*, not bold, centred; table caption **above** the table, figure caption **below** the figure |
| A16 | In-text references to figures, tables, algorithms and equations | Plain text | *Italic*, not bold (e.g. *Table 4.2*, *Figure 6.1*, *Equation (6.3)*) |
| A17 | Tables | Several split across pages (1.1, 1.2, 4.2, 4.4, 5.3 and others) | Every row set to "keep with next" and "do not split"; all 46 content tables verified by Word to start and end on the same page as their caption. Header row bold with light grey shading; body TNR 12 pt |
| A18 | Table of Contents | Visible table, page numbers in two fonts, many wrong, entries not matching headings | Invisible borders (0 opacity); chapter rows bold; 1.1 entries indented 0.25 in and 1.1.1 entries 0.55 in; page numbers are live Word PAGEREF fields, so they always match the pages |
| A19 | List of Figures / List of Tables | Visible borders; algorithms mixed into the table list; stale page numbers | Invisible borders; live page numbers; algorithms grouped under an "Algorithms" heading at the end of the List of Tables |
| A20 | Equations | Low-resolution images labelled `Equation(6.1)`, `(6.3)`, `Equation 6.5`, some below the formula | Native Word equations (vector, sharp at any zoom), centred, with `(6.n)` right-aligned on the same line |
| A21 | Diagrams | Figures 5.1, 6.1 and 6.2 were blurry images; Figures 8.1 and 8.2 low resolution | All five redrawn at 300 dpi (`report/v3_build/make_figures.py`), same layout and labels, updated to the current system |
| A22 | Algorithms 7.1 to 7.4 | Broken line wraps (step 4 glued to step 3, step 10 to step 9) | Boxed, Consolas 10 pt, one numbered step per line, kept on one page |
| A23 | References | Mixed author formats; venue not italic; [4] and [5] venues wrong | IEEE style with hanging numbers; journal and conference names in *italic*; details taken from `IEEE-Paper/references.bib` ([4] is a preprint, [5] is arXiv:2409.08916) |
| A24 | Consistency | British and American spelling mixed; "percent", "per cent" and "%"; "Grok" | British spelling; "%" after numbers; "Groq" everywhere |
| A25 | Voice | we ×12, our ×14, us ×4, you/your ×5, "he or she", "his/her" in the chapters | None left outside the Acknowledgement and the standard Declaration (checked automatically) |
| A27 | Sections across pages | About 35 sections started at the bottom of one page and continued on the next | Every section that fits on one page is kept whole (heading and text move to the next page together); found by measuring the laid-out pages in Word and repeated until nothing changed. Only sections longer than a full page still continue onto the next page |

## B. Data updated from the current project (`TESTING.md`, `progress.md`, `IEEE-Paper/paper_content.tex`)

| Item | Original report | Fixed copy | Source |
|---|---|---|---|
| Automated tests | 48 tests (pytest), all passing, about 103 s | 373 tests (backend 305: unit 162, integration 71, functional 3, security 59, non-functional 10; real-model 4; Vitest 52; Playwright 12), all passing | progress.md 2026-11-22/23, paper Table V |
| Dense retrieval model | BGE-base-en, 768-d | bge-m3, 1024-d on a GPU; BGE-base-en, 768-d on a CPU | paper §V-B |
| Reranker | MiniLM cross-encoder | bge-reranker-v2-m3 on a GPU; MiniLM on a CPU | paper §V-B |
| Candidates per retriever | 15 | 20 | paper §V-E |
| Last retrieval stage | Hard filter to the diagnosed disease | Soft topic preference (+0.1) and near-duplicate removal | progress.md 2026-11-22 |
| Knowledge base size | not stated | 14 PDF documents, 931 passages | paper §V-A |
| LLM fallback | Gemini, then Groq, then retrieved text | Gemini 2.5 Flash, then gpt-oss-120b on Groq, then an offline guide with the retrieved text | paper §V-G |
| Language routing | Regex pre-router only | LLM router (JSON mode, sees last two exchanges); Unicode regex as fallback | progress.md 2026-11-22 |
| Weather | Temperature, humidity, rainfall | Also elevation and a three-day forecast; high / moderate / low risk level; spray window | paper §V-F |
| Confidence gate | 75% | 75%, plus "uncertain" when the best passage scores below 0.60 | paper §IV-D |
| Image storage | Base64 inside the database | Sanitised files on disk; upload guard strips metadata | docs/modules/module-4, paper §IV-B |
| Marketplace | Price slider, keyword | Unit normalisation to kg and Rs./kg; up to 8 photos; variety, distance, lot-size filters | paper §VII |
| CNN accuracy | ~90% validation, ~80% new leaves | Kept, plus leak-free 5-fold CV: accuracy 97.9%, macro-F1 0.970, Phoma F1 0.949, gate answers 99.3% at 98.1% | paper §IX-B |
| Response times | Warm inference 14.2 ms; suite 103 s | GPU 5.3 ms, CPU 54.9 ms, retrieval ≈0.4 s, complete advisory ≈6 s, chat turn 0.22 s (cache hit 0.85 ms and cold start 704 ms kept: no newer measurement) | TESTING.md, paper §IX-A/D |
| Benchmarks | none | Retrieval Recall@3 0.867 vs 0.500; correctness 0.944 / 0.824 / 0.611; unsupported doses 0% vs 20.4%; chatbot 43/43 vs 15/43, correctness 0.91 vs 0.38 (new Table 8.4) | progress.md 2026-11-22 |
| Hardware | NVIDIA RTX GPU | NVIDIA RTX 3070 Laptop GPU | progress.md Phase 0 |

## C. Content added or restored

- **Section 1.5.4** heading restored (its text had been merged into 1.5.3).
- **Section 3.8** renamed "Summary of the Literature Surveyed" (was wrongly numbered 3.1); **Section 3.9** "Research Gap" (was "3.2 Overall Research Results:"), garbled sentences rewritten.
- **Literature survey:** "Positives" → "Advantages" and "Drawbacks" → "Disadvantages" in all seven papers.
- **Section 8.4 Deviations and What Was Learned** with 8.4.1 to 8.4.6 (cold start, cache-key collisions, missed percentages, empty LLM replies, quota, chatbot faults), written from `progress.md` and the paper. These sections were listed in the old TOC and cross-referenced in 7.8, but missing from the body.
- **Section 8.5 Field Feedback** (from the existing field-test statements; no new claims).
- **Section 8.6 Comparison with Common Alternatives:** heading restored, benchmark paragraph and **Table 8.4** added. The old risk table becomes **Table 8.5**.
- One lead-in sentence added before every table, figure and algorithm that was not mentioned before it (Tables 3.1, 4.2, 4.3, 4.4, 5.2 to 5.5, 7.1, 7.3, 8.1, 8.2, 8.4, 8.5, 9.1, 9.2, 9.4, A.1, C.1, D.1 and Algorithms 7.1 to 7.4). All 40 captions were then checked automatically.
- **Chapter 8 citations removed:** "the Grenze CNN [3]" and the reference to "RAG-based coffee remediation".
- **Algorithms 7.2 to 7.4** updated to the current pipeline (top 20, soft preference, offline fallback, router with history, unit normalisation).

## D. Items deliberately not changed

- Certificate signatories (Registrar), as you asked.
- The Declaration's standard "We hereby declare … by us" wording, as you asked.
- Table 1.3 row 4 and Section 1.5.4 keep "about 90% / about 80%", because they record what was shown at the reviews.
- CNN cold start (704 ms) and cache hit (0.85 ms): no newer measurement exists in the project, so the original values are kept.
- Sprint plan (Table 6.2) and the Phase 2 history are unchanged.
