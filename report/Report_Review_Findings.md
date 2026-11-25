# Report review: formatting rules and fixes to approve

Report reviewed: `report/Team_35_report_aligned_v2.docx` / `.pdf` (68 pages)
Reference used: `report/Perfect.pdf` (89 pages)
Status: **nothing has been changed yet.** Every item below needs your OK first.

---

## Part A. Formatting rules taken from the reference report

Measured from the reference PDF: font, size, bold or italic, alignment and position of every line.

### A1. Page header and footer (Chapter 1 onwards only)
| Element | Rule from the reference |
|---|---|
| Header, left | Project title, Times New Roman 10 pt, regular |
| Header, right | PES University logo |
| Under the header | A full-width horizontal rule |
| Above the footer | A full-width horizontal rule |
| Footer, left | `Dept. of CSE`, TNR 10 pt |
| Footer, centre | `August - November, 2026`, TNR 10 pt |
| Footer, right | `Page No.1`, `Page No.2`, … TNR 10 pt |
| Front matter (cover to List of Tables) | No header, no footer, no page number |
| Numbering | Restarts at 1 on the first page of Chapter 1 |

### A2. Headings
| Element | Font | Size | Style | Alignment |
|---|---|---|---|---|
| `CHAPTER 1` line | TNR | 18 | Bold | **Left** |
| Chapter title (`INTRODUCTION`) | TNR | 18 | Bold, uppercase | Centre, on its own line under `CHAPTER 1` |
| Level 2 (`1.1 Background`) | TNR | 16 | Bold, Title Case | Left |
| Level 3 (`1.1.1 Plagiarism`) | TNR | 14 | Bold, Title Case | Left |
| Front-matter titles (DECLARATION, ACKNOWLEDGEMENT, ABSTRACT, TABLE OF CONTENTS, LIST OF FIGURES, LIST OF TABLES, REFERENCES, APPENDIX) | TNR | 18 | Bold, uppercase | Centre |
| Every chapter | Starts on a new page | | | |

### A3. Body text and spacing
- Times New Roman 12 pt, regular, 1.5 line spacing.
- Spacing: about 6 pt between paragraphs, about 18 pt before a level-2 heading and 12 pt before a level-3 heading, 6 pt after both.
- Bold is used only for: headings, the label at the start of a list item (`**Code Copying and Reuse:** text…`), table header rows, and key result figures.
- Italic is used only for: figure and table captions, journal or conference names in references, and (your rule) in-text references to figures and tables.

### A4. Lists (indentation follows the numbering)
- Numbered list: number at 0.25 in (18 pt) from the margin, text and wrapped lines hang at 0.5 in (36 pt).
- Bullet list: same positions, round bullet (●).
- A list item that starts with a label: label in **bold** ending in a colon, rest in regular text.

### A5. Figures and tables
| Element | Rule |
|---|---|
| Figure caption | **Below** the figure, TNR 10 pt, *italic*, **not bold**, centred |
| Table caption | **Above** the table, TNR 10 pt, *italic*, **not bold**, centred |
| Table header row | TNR 12 pt bold |
| Table body | TNR 12 pt regular |
| Figure | Centred |
| In-text reference | `Figure 5.1` / `Table 4.2` in *italic*, not bold (your rule) |

### A6. Front matter
| Page | Rule from the reference |
|---|---|
| Cover | Arial. "Dissertation on" 16 pt bold italic; project title 16 pt bold in quotes; "Submitted in partial fulfilment…" 12.5 pt italic; degree lines 16 pt bold; "Submitted by:" 12 pt bold italic; names and SRNs 12 pt bold; "Under the guidance of" 12 pt italic; guide name TNR 14 pt bold, designation TNR 14 pt; department block Arial 12 pt, address 10 pt |
| Certificate | Arial. "CERTIFICATE" 20 pt bold; title 14 pt bold; body 10 pt; signature block 10 pt |
| Declaration | Title TNR 18 bold; body **TNR 14**; project title, degree and university in bold; SRN, name and a signature line `__________` in 14 pt bold |
| Acknowledgement | Title TNR 18 bold; body **TNR 14**; first person **singular** ("I would like to…") |
| Abstract | Title TNR 18 bold; body TNR 12 |
| TOC | Title TNR 18 bold. Chapter entries bold uppercase; 1.1 entries indented 18 pt, 1.1.1 entries indented 36 pt; dot leaders; page numbers right-aligned. All TNR 12 |
| List of Figures / Tables | Title TNR 18 bold; entries TNR 12 |

### A7. References
- Title `REFERENCES`, TNR 18 bold, centre.
- IEEE style: `[1]` at 0.25 in, text hanging at 0.5 in; author initials before surname; article title in "quotes"; journal or conference name in *italic*; vol., no., pp., year.

### A8. Places where the reference contradicts itself (I'll pick one consistent option)
- Its TOC switches from TNR 12 to Arial 11 halfway through, and its reference list is in Arial 11. **Plan: TNR throughout the body, TOC and references.**
- It numbers figures as `Figure 1.` across the whole report. Your report numbers by chapter (`Figure 5.1`). **Plan: keep chapter numbering, styled `Figure 5.1: Caption`.**
- One of its tables splits across two pages. Your rule overrides it: **no table splits.**
- Its body text is left-aligned (ragged right); yours is justified. **This is decision 2 below.**
- The reference is US Letter size (8.5 × 11 in). Yours is A4. **Plan: keep A4** (the PES standard).

---

## Part B. Your rules (as I will apply them)
1. No *we*, *our*, *us*, *I*, *you* anywhere outside the Acknowledgement; rewrite those sentences in passive voice. (Found: we ×12, our ×14, us ×4, you/your ×5, "he or she" ×1, "his/her" ×1.)
2. The Acknowledgement starts with "I" and stays first-person singular throughout.
3. List of Figures and List of Tables (and TOC) tables: borders set to none (0 opacity).
4. Indentation follows the numbering (TOC levels and lists).
5. No table splits across pages: header row repeated is not enough; each table is kept whole ("keep with next" on every row; long tables move to the next page).
6. Consistent spacing above and below headings, captions, tables, figures and equations.
7. No citations or references to papers in Chapter 8 (Results).
8. Literature survey: "Positives" → "Advantages".
9. Every figure and table is mentioned in the text **before** it appears. No unmentioned figure or table.
10. "Summary of the Survey" → "Summary of the Literature Surveyed".
11. Grammar corrected.
12. Equation number on the same line as the equation, right-aligned: equation centred, `(6.1)` flush right.
13. All diagrams redrawn as sharp, high-resolution images.
14. All equations rebuilt as real Word equations (vector, sharp at any zoom).
15. Edit only the wrong lines; leave correct sentences untouched.
16. Sentences that make no sense are rewritten or removed.
17. Header and footer exactly in the reference pattern (A1).
18. Work on a copy; the original stays untouched.
19. Every change recorded in a change log for you to review.

---

## Part C. New problems found (not on your list)

### C1. The .docx itself is broken
The .docx is a PDF-to-Word conversion: **68 sections (one per page), text inside floating frames, and parts of sentences hidden behind text boxes.**
Examples: "retrieval-augmented engi⟶n by a Kannada…", "personalise⟶l recommendations", "in mult," (truncated).
"Phase - 3" in the Acknowledgement has also become a numbered list item "3.".
Patching this file will keep breaking. **Plan: rebuild the copy as a clean Word document** (real heading styles, an automatic TOC, real caption numbering, one header/footer, real equations), carrying over every word, edited only where listed. (Decision 1.)

### C2. Table of Contents, List of Figures, List of Tables
- Page numbers are in two different fonts (half are LiberationSerif) and many are stale (e.g. 8.4 shows page 39 after 8.3 on page 43).
- TOC entries do not match the headings in the body:
  - 3.1.1 "Idea and pipeline" (body: "Abstract")
  - 3.9 "Research Gap" (body: "Overall Research Results:")
  - 6.5.1 "Why we invested in automated testing" (body: "Use of Automated Testing")
  - 9.3 "What We Take Away" (body: "Take Away")
  - List of Tables 7.2 "Who tested what" (caption: "Individual contribution towards testing")
- **TOC lists sections that are missing from the body:** 8.4 "Deviations and What We Learned" with 8.4.1–8.4.5 (cold start, cache-key collisions, missed percentages, empty LLM replies, quota) and 8.5 "Field Feedback". Section 7.8 also points to "Section 8.4/8.5/8.6" for these. (Decision 4.)
- Literature review entries show sub-sections only for 3.1.
- Algorithms 7.1–7.4 are mixed into the List of Tables. **Plan: keep them there under a separate "Algorithms" group, or give them their own list.**
- Heading numbering in the body mixes automatic and typed numbers (e.g. "1.5.5" typed by hand). 1.5.4 has no heading; its text is merged into 1.5.3.

### C3. Header, footer, page numbers
- Header title is 8 pt across two lines (reference: 10 pt). The full title is too long for one line at 10 pt, so it will use 2 lines at 10 pt.
- Footer shows `Aug – Nov 2026` and a bare number (reference: `August - November, 2026` and `Page No.N`).
- Page 13 (Chapter 1, page 1) prints two page numbers ("2" and "1").
- No rule above the footer.

### C4. Captions
- All captions are bold 11 pt (rule: italic, non-bold, 10 pt).
- Captions for Tables 1.3, 5.2, 5.3 and Figure 5.1 are justified instead of centred.

### C5. Tables split across pages
These currently break across pages: Tables 1.1, 1.2, 4.2, 4.4, 5.3 (and any that move once the text is fixed). All will be kept whole.

### C6. Figures and tables with no mention before them
- **No mention at all:** Tables 3.1, 4.2, 4.3, 4.4, 5.2, 5.3, 5.4, 5.5, 7.1, 8.1, 8.2, 8.4, 9.1, 9.2, 9.4, A.1, C.1, D.1, and Algorithms 7.1–7.4.
- **Mentioned only after the table/figure:** Table 7.3, Table 8.3, Figure 8.2.
- One short lead-in sentence will be added before each (e.g. "The functional requirements are listed in *Table 4.1*.").

### C7. Diagrams, equations, algorithms
- Figure 5.1 (architecture), 6.1 (retrieval pipeline) and 6.2 (speech chain) are blurry raster images. 8.1 and 8.2 are charts.
  **Plan: redraw all five as crisp, high-resolution images, same content and labels.**
- Equations 6.1–6.5 are low-resolution images. Their labels are inconsistent: `Equation(6.1)`, `(6.3)`, `Equation 6.5`. Some sit below or beside the formula. The Haversine equation (6.5) is partly hidden.
  **Plan: all become Word equations with `(6.n)` right-aligned on the same line.**
- Algorithm boxes 7.1–7.4 have broken line wraps (e.g. step "4." glued to the end of step 3, "10. RETURN" glued to step 9).
  **Plan: rebuild as clean numbered boxes, Courier/Consolas 10 pt, one step per line.**
- Page 42 has a large blank gap before Figure 8.1.

### C8. Consistency
- **Spelling:** a mix of British and American (organise/organize, behaviour/behavior, recognise/recognize, generalisation/generalization, fertiliser/fertilizer).
  **Plan: British spelling throughout** (Indian academic convention; most of the report already uses it).
- **Percentages:** "percent" ×22, "per cent" ×2, "%". **Plan: use "%" with numbers** (90%, 75%).
- **"Grok"** appears 3 times; it should be **Groq**.
- **Heading case:** a mix of sentence case and Title Case ("Classification head and softmax", "Generating The Answer"). **Plan: Title Case everywhere**, as in the reference.
- **Lists:** the 9 request-flow steps, the objectives and the limitations use inconsistent indents. The Chapter 9 "Step 1…Step 4" lines are broken, with Steps 2 and 3 on one line.
- **Double full stops:** "consequences..", "field..", "considerably..", "district..", "time on task..".
- **Missing spaces:** "buyers.Growers", "deviation.This", "benefits.It", "source.It", "recordings .It".
- **Dashes:** "Aug - Nov" vs "Aug – Nov." Use one form.

### C9. Sentences that make no sense (will be rewritten, meaning kept)
Representative list. Every one, with before and after, will be in the change log.

| Where | Current text | Problem |
|---|---|---|
| Abstract | "small farmers are deprived of timely … advice … and able to reach the buyers without the intermediaries" | States the opposite of what is meant |
| 1.1 | "If leaf rust or leaf miner do poorly a season, the family may have a poor season." | Meaning reversed |
| 1.1 | "it is not consistent and unrecordable" | Broken grammar |
| 1.3 | "the classifier was able to process an image at the end of that period … At the end of this period" | Repeated phrase |
| 1.5.1 | "Both have been modified through our approach … between the advice and the grower." | Garbled |
| 1.5.2 | "each of the two classifiers had slightly different conceptions … Both modules are scanned in the same way" | Wrong subject; garbled |
| 1.5.5 | "It took longer to make this happen. than wiring." | Broken sentence |
| 3 (intro) | "Each will build a component … basis-informed advice" | Garbled |
| 3.5 | "Chat is a conversational…", "Farmer.To resolve … the Chat uses" | "Farmer.Chat" split apart |
| 3.4 | "There are a number of reasons why the reported performance gains are found to come from different research contexts" | No meaning |
| 3.6 | "By comparing several machine learning algorithms, you can identify…" | Second person |
| 3.9 | "Label is right down to the diagnosis", "and it's left to the reader!", "If you must perform the test right and do it wrong if you don't…", "there was no chain of coffee language" | Whole paragraph garbled |
| 4.1 | "This chapter is a list of what is expected to happen and when to expect it at PlantIQ." | No meaning |
| 4.2.2 | "Use real microclimate data for Phase 2 instead of the simulated data." | Wrong phase |
| 4.5.1 | "JMuBEN is a set of Arabica-specific coffee for use against rust", "leaves that the model has never photographed" | Garbled |
| 4.5.3 | "the weather was added as a coordinate", "it is tested by a test" | Garbled |
| 4.7 | "so diagnosis must require a connection" | Garbled |
| 4.8 note | "It has not been measured from farmers' recordings .It was not measured it on farmers' recordings" | Duplicated |
| 5.3 | "Classifier verifies a cache for SHA-256", "Viewings are sorted by distance" | Wrong words |
| 5.4 | "Failure to any external dependency." "If the model doesn't know, be honest." | Fragments |
| 5.6.3 | "three speed levels of speech detection" | Wrong: it is a three-tier fallback |
| 6.1.5 | "the model is correct 80 percent of the time" | Should be 75% (the gate) |
| 6.2.2 | "The learning model was not used here, This can be…" | Run-on |
| 6.2.5 | Duplicated sentence "The advisory is marked as Verified … It means that the advisory is marked Verified…" | Duplicate |
| 6.2.5 | "answers given in the hallucination condition produced a 6.7 percent hallucination rate" | Should be "answers generated with retrieval" |
| 6.3.1 | Italic paragraph with "Can I Spray Now, How Much Does It Cost Me For The Small Plot" | Wrong case and italics; "what the previous person had said" |
| 6.3.3 | "replaced by a three-tiered browser recogniser" | Wrong: the tiers are not browser-based |
| 6.3.4 | "size of the trade window", "the added turns be at least 10" | Should be the context window and turns |
| 6.4.2 | "this is where poor data might otherwise infiltrate the buyer's eyes" | Informal |
| 6.5.1 | "they would never have been able to be integrated" | Garbled |
| 6.5.3 | "since they are just the number of personal laptop used" | Garbled |
| 7.2 | "The fallback chain was a test chain; It was not possible to test it without invoking it…" | No meaning |
| 7.4 | "leads to the next failure" | Should be "next fallback" |
| 7.7 | "for t modules" | Truncated |
| 7.8 | "Some GPUs tests" | Grammar |
| 8.2 | "the paper in the field image is warned by the Grenze CNN [3]" | No meaning; also a citation in Results |
| 9 | "It concludes it as a unified pipe" | Garbled |
| 9.3 | "more safe than grounding", "let four modules to be integrated" | Grammar |
| 9.6 | "Leaf Sought out measured, not modeled conditions." | Garbled heading ("Leaf wetness: measured, not modelled") |
| 9.6 | Graph-based reasoning paragraph ends mid-sentence ("the restrictions on those") | Truncated |
| App. B | "If not, click on the picture again", "Listings are restricted by distance", "attention-grabbing captions" | Logic inverted; wrong words |

Plus the line-level grammar fixes across all chapters: subject–verb agreement ("The system use", "Zhao et al. presents", "examined result show"), "3 type of disease", "treatment advices", "outcompared", and others.

### C10. Citations in the Results chapter (your rule 7)
- 8.2: "the Grenze CNN [3]" → removed.
- 8.3 (comparison): "the one used in RAG-based coffee remediation" (paper [1]) → reworded without citing the paper.

### C11. Literature survey structure
- Each paper uses Abstract / Research Gap / Positives / Drawbacks.
  **Plan:** Positives → **Advantages** (your rule), and Drawbacks → **Disadvantages** to pair with it, as the reference does.
- "Summary of the Survey" → **Summary of the Literature Surveyed**; "Overall Research Results:" (stray colon) → a proper Research Gap heading, matching the TOC.

### C12. Front matter
- Acknowledgement: "We/us/our" → "I/me/my"; the "3." list artifact is removed; "influenced our perspective on the next generation" is rewritten.
- Declaration: uses "We hereby declare … carried out by us". (Decision 3.)
- Cover, Certificate and Declaration sizes differ from the reference (A6). Example: the cover uses TNR 13 and 10 pt; the reference uses Arial 16 and 12 pt.
- The Declaration has no signature lines.
- The Certificate's third signatory is "Dr. Sridhar K S, Registrar"; the reference has "Dr. B K Keshavan, Dean of Faculty". **Please confirm which is correct for your batch; I won't change it unless you say so.**

### C13. References
- The authors of [1] are written out in full with "Dr."; the other entries use initials.
- Venue names are not italic; [5] says only "ACM Proceedings".
- **Plan:** IEEE format for all 7 entries, using the bibliographic data already in `IEEE-Paper/references.bib`.

### C14. Report data is out of date
The report still says **48 tests**, ~90% / ~80% accuracy, BGE-base-en, 704 ms cold start, and so on.
The project now records:
- **354/354 tests** (TESTING.md)
- bge-m3 retrieval
- CNN 5.3 ms GPU / 54.9 ms CPU
- out-of-fold macro-F1 0.975
- the RAG and chatbot benchmarks from November
(Decision 5.)

---

## Part D. Decisions needed from you
1. **Rebuild** the copy as a clean Word document (recommended), or patch the converted file in place?
2. **Body alignment:** justified (as now), or left-aligned like the reference?
3. **Declaration:** keep the standard "We hereby declare…" wording, or make it passive ("It is hereby declared that the project … has been carried out by the undersigned")?
4. **Missing sections 8.4 and 8.5** (Deviations, Field Feedback): write them from the project records (progress.md has all five bugs), or remove them from the TOC and fix the cross-references?
5. **Latest data:** update the numbers, tables and Chapter 8 to the current project (354 tests, benchmarks), or keep the numbers as they are?
6. **Certificate signatory:** Registrar (as now) or Dean of Faculty?

## Part E. What you will get after approval
- `report/Team_35_report_v3.docx` and `report/Team_35_report_v3.pdf`: the fixed copy (originals untouched).
- `report/Report_Change_Log.md`: every change listed as *section · before · after · rule applied*.
- A page-by-page check of the final PDF: no split tables, every figure and table mentioned before it appears, no first person outside the Acknowledgement, equation numbers on the same line, and headers and footers on every page.
