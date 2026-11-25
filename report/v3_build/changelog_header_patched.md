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
| A17 | Tables | Several split across pages (1.1, 1.2, 4.2, 4.4, 5.3 and others) | Every row set to "keep with next" and "do not split"; every content table verified by Word to start and end on the same page as their caption. Header row bold with light grey shading; body TNR 12 pt |
| A18 | Table of Contents | Visible table, page numbers in two fonts, many wrong, entries not matching headings | Invisible borders (0 opacity); chapter rows bold; 1.1 entries indented 0.25 in and 1.1.1 entries 0.55 in; page numbers are live Word PAGEREF fields, so they always match the pages |
| A19 | List of Figures / List of Tables | Visible borders; algorithms mixed into the table list; stale page numbers | Invisible borders; live page numbers; algorithms grouped under an "Algorithms" heading at the end of the List of Tables |
| A20 | Equations | Low-resolution images labelled `Equation(6.1)`, `(6.3)`, `Equation 6.5`, some below the formula | Native Word equations (vector, sharp at any zoom), centred, with `(6.n)` right-aligned on the same line |
| A21 | Diagrams | Figures 5.1, 6.1 and 6.2 were blurry images; Figures 8.1 and 8.2 low resolution | All five redrawn at 300 dpi (`report/v3_build/make_figures_old.py`) with the same content and labels as the original |
| A22 | Algorithms 7.1 to 7.4 | Broken line wraps (step 4 glued to step 3, step 10 to step 9) | Boxed, Consolas 10 pt, one numbered step per line, kept on one page |
| A23 | References | Mixed author formats; venue not italic; [4] and [5] venues wrong | IEEE style with hanging numbers and initials; journal and conference names in *italic*; the original venue details are kept |
| A24 | Consistency | British and American spelling mixed; "percent", "per cent" and "%" | British spelling; "%" after numbers |
| A25 | Spelling of Groq | "Grok" in 3 places | "Groq" everywhere |
| A26 | Voice | we ×12, our ×14, us ×4, you/your ×5, "he or she", "his/her" in the chapters | None left outside the Acknowledgement and the standard Declaration (checked automatically) |
| A27 | Sections across pages | About 35 sections started at the bottom of one page and continued on the next | Every section that fits on one page is kept whole (heading and text move to the next page together); found by measuring the laid-out pages in Word and repeated until nothing changed. Only sections longer than a full page still continue onto the next page |

## B. Data

No data was changed. Every number, model name and test count is the one in the original report; only wording, grammar, voice, structure and formatting were fixed. The only factual-looking edits are spelling corrections ("Grok" → "Groq") and section numbers that were wrong in the original.

## C. Content added or restored

- **Section 1.5.4** heading restored (its text had been merged into 1.5.3).
- **Section 3.8** renamed "Summary of the Literature Surveyed" (was wrongly numbered 3.1); **Section 3.9** "Research Gap" (was "3.2 Overall Research Results:"), garbled sentences rewritten.
- **Literature survey:** "Positives" → "Advantages" and "Drawbacks" → "Disadvantages" in all seven papers.
- **Section 8.4 Deviations and What Was Learned** with 8.4.1 to 8.4.5 (cold start, cache-key collisions, missed percentages, empty LLM replies, quota), written only from facts already stated in the original report. These sections were listed in the old TOC and cross-referenced in 7.8, but missing from the body.
- **Section 8.5 Field Feedback** (from the existing field-test statements; no new claims).
- **Section 8.6 Comparison with Common Alternatives:** heading restored (its text and Table 8.3 were already in the original).
- One lead-in sentence added before every table, figure and algorithm that was not mentioned before it (Tables 3.1, 4.2, 4.3, 4.4, 5.2 to 5.5, 7.1, 7.3, 8.1, 8.2, 8.4, 9.1, 9.2, 9.4, A.1, C.1, D.1 and Algorithms 7.1 to 7.4). All 39 captions were then checked automatically.
- **Chapter 8 citations removed:** "the Grenze CNN [3]" and the reference to "RAG-based coffee remediation".
- **Algorithms 7.1 to 7.4**: same steps as the original, with the broken line wraps fixed.

## D. Items deliberately not changed

- Certificate signatories (Registrar), as you asked.
- The Declaration's standard "We hereby declare … by us" wording, as you asked.
- All original data, including the 48 tests, BGE-base-en retrieval, top 15 candidates, 90% / 80% accuracy and the response times.
- Reference venues for [4] and [5] are kept as in the original, although `IEEE-Paper/references.bib` lists [4] as a preprint and [5] as arXiv:2409.08916.
- Sprint plan (Table 6.2) and the Phase 2 history are unchanged.
