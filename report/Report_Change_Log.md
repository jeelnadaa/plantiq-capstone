# Report change log

Original: `report/Team_35_report_aligned_v2.docx`. Fixed copy: `report/Team_35_report_v3.docx` and `.pdf`.
The original files were not modified.

How to read this log: ~~struck-through words~~ were removed, **bold words** were added. Every body paragraph that changed is listed under its section, with the full new text and the marked difference. Paragraphs that are not listed were carried over word for word. Section A lists the formatting changes that apply to the whole document; Sections B to D list the content changes.

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


## Front matter text changes (Acknowledgement and Abstract)

### Acknowledgement

- **Changed:** ~~We~~ **I** would like to express ~~our~~ **my** gratitude to Prof. Deepti C., Assistant Professor, Department of Computer Science and Engineering, PES University, for her continuous guidance, assistance and encouragement throughout the development of this UE23CS441A Capstone Project Phase - 3. The feedback she gave ~~us~~ **me** across all three project reviews pushed ~~us~~ **me** to treat the work as an engineering exercise and not only **as** a demonstration. ~~We are~~ **I am** grateful to the Capstone Project Coordinator, Dr. Vandana M. Ladwani, Associate Professor, Department of Computer Science and Engineering, PES University, for organising, managing and helping with the entire process. ~~We~~ **I** take this opportunity to thank Dr. Sandesh B J, Chairperson, Department of Computer Science and Engineering, PES University, for all the knowledge and support ~~we~~ **I** have received from the department. ~~We~~ **I** would like to thank Dr. Sridhar K S, Registrar, PES University, for his help. ~~We are~~ **I am** deeply grateful to Late Dr. M. R. Doreswamy, Founder, PES University, whose vision and dedication continue to inspire generations of learners. ~~We~~ **I** would like to express ~~our~~ **my** sincere gratitude to Prof. Jawahar Doreswamy, Chancellor, PES University, Dr. Suryaprasad J, ~~Vice- Chancellor,~~ **Vice-Chancellor,** PES University, and Dr. Nagarjuna Sadineni, Pro Vice-Chancellor, PES University, for providing ~~us~~ **me with** various opportunities and enlightenment every step of the way. ~~We are~~ **I am also** grateful ~~also~~ to the coffee planters ~~that~~ **who** were willing to test the application and ~~provided us with~~ **gave** their ~~true feedback~~ **honest feedback,** which ~~influenced our perspective on~~ **shaped the direction of** the next ~~generation.~~ **version.** Last but by no means least, this project would not have been possible without the ~~on-going~~ **ongoing** support and encouragement ~~we~~ **I** have received from ~~our~~ **my** family and friends.

### Abstract

- **Changed:** While Karnataka is the leading producer of coffee in India, ~~the~~ **its** small farmers ~~are deprived of~~ **lack** timely ~~and~~ **advice on leaf diseases in their** local language ~~advice on the leaf diseases~~ and ~~able~~ **have little direct access** to ~~reach the~~ buyers without ~~the~~ intermediaries. ~~A~~ **Diagnosis, advice, conversation and market access are brought together in one application. Five leaf conditions are identified by a** fine-tuned ~~ResNet-50 identifies five leaf conditions, scoring~~ **ResNet-50, which scores** about 90% on validation ~~images and~~ **images,** about 80% on unseen ~~leaves.~~ **leaves and 97.9% in a leak-free cross-validation on public images.** Its result ~~feeds~~ **is passed to** a hybrid ~~retrieval- augmented~~ **retrieval-augmented** advisory engine that combines FAISS, BM25, rank fusion, a cross-encoder reranker and live weather, and **each answer is labelled Verified or Caution by** a dosage ~~audit labels each answer Verified~~ **audit. Voice** or ~~Caution. A~~ **text input is accepted by a** Kannada and English ~~chatbot accepts voice or text,~~ **chatbot,** and **listings are sorted by distance in** a direct marketplace ~~sorts listings by distance~~ with one-tap Maps, call and WhatsApp. **On 75 coffee questions, the supporting evidence is found by the hybrid retriever for 87% of questions, against 50% for dense-only retrieval.** All ~~48~~ **373** automated tests ~~pass in about 103 seconds;~~ **pass;** one latency target, the first CNN call after start-up (704 ms), was missed.


## E. Paragraph-by-paragraph text changes (Chapters 1 to 9, references, appendices)

### 1.1 Coffee Cultivation in Karnataka

- **Changed:** Nearly ~~70 per cent~~ **70%** of the coffee grown in India is produced in Karnataka. Most of it ~~is~~ **comes** from small family farms scattered across Kodagu, ~~Chikmagalur, Hassan~~ **Chikmagalur and Hassan,** and for these families ~~it~~ **coffee** is not a sideline but the primary ~~crop, coffee.~~ **crop.** If leaf rust or leaf miner ~~do poorly~~ **takes hold in** a season, the family may have a poor ~~season.~~ **year.**
- **Changed:** In such farms, much knowledge concerning the daily workings of the farm is passed on by word of mouth: one neighbour recalls ~~the same~~ **similar leaf** patches ~~growing~~ **appearing** the previous year; one relative is enthusiastic about a certain spray and another about a particular ~~fertilizer;~~ **fertiliser;** the estate manager has an idea of what the weather will do. This experience is useful, but it is ~~not consistent~~ **inconsistent** and ~~unrecordable.~~ **unrecorded.** It is also not accessible when the closest extension officer is located two valleys ~~away,~~ **away** and an infection is already ~~underway.~~ **under way.**

### 1.2 About PlantIQ

- **Changed:** PlantIQ started from a simple question. What would it take for a grower to point a phone at a sick leaf, get back something they can act on in the language they speak at home, and then use the same phone to offer the harvest to a buyer? ~~An~~ **That question cannot be answered by an** image classifier ~~alone cannot answer that.~~ **alone.** A label such as "Leaf Rust" says little until it is tied to this week's weather, a suitable treatment, a safe quantity and, eventually, a buyer.
- **Changed:** ~~Our approach~~ **The problem** has **been** divided ~~the problem~~ into four modules, summarised in Table 1.1. Perception is handled by a computer-vision model, advice by a retrieval-augmented engine, conversation by a Kannada and English chatbot, and the market by a direct listing and discovery module.

### 1.3 Progress Up to Phase 2

- **Changed:** Phase 1 ~~has included~~ **covered** identifying the scope, reading the ~~literature and~~ **literature,** verifying ~~the~~ access to the ~~tools,~~ **tools and** APIs, and ~~check if~~ **checking whether** the data was available. During Phase 2 every module was constructed by a different team member and was ~~individually tested. At the end of this period, the classifier was able to process an image at~~ **tested individually. By** the end of that ~~period~~ **period, the classifier could process an image** through a FastAPI endpoint, ~~Structured~~ **structured** advisories were ~~written to~~ **produced by** the retrieval pipeline with simulated weather, listings were stored and mapped in the marketplace, and the chatbot was ~~basic~~ **basic,** with English voice input. The modules were not communicating with each other, the speech recognition system achieved only ~~55 percent~~ **55%** word accuracy ~~with~~ **on** Kannada words in the disease ~~word set,~~ **vocabulary,** the weather values were simulated and no actual users had used the system. ~~We also predicted that~~ Phase 3 ~~would~~ **was also expected to** be the most critical and high-risk ~~phase for~~ **phase, because of** integration.

### 1.5 Feedback from Reviews 1 and 2

- **Changed:** The first two reviews provided ~~us with~~ five concrete suggestions. Each was ~~initially~~ rated for feasibility when **it was** received and ~~it~~ was followed through to ~~our~~ **the** final review. ~~The~~ **A** brief version is provided in Table 1.3, and the subsections below describe what was actually done.

### 1.5.1 Local Language Integration

- **Heading:** `1.5.1 Local language integration` → `1.5.1 Local Language Integration`
- **Changed:** Greater emphasis ~~was requested by the reviewers~~ on making Kannada an integral part of the ~~product~~ **product,** rather than ~~treating it as~~ an ~~add-on. Subsequently we planned~~ **add-on, was requested by the reviewers. The earlier plan was** to translate English advice ~~to~~ **into** Kannada and ~~then use~~ **to take** voice ~~input, which was reliant on~~ **input through** a browser speech API that was not very good with disease vocabulary. Both have **since** been ~~modified through our approach.~~ **changed.** The first choice **for speech is** now ~~is~~ a local speech model, with cloud ~~fallback subsequently;~~ **fallbacks behind it;** Kannada text ~~gets treated~~ **is handled** by having the language model answer directly in Kannada script, **so that no translation step sits** between the advice and the grower.

### 1.5.2 A Standard Input for RAG and CNN

- **Heading:** `1.5.2 A standard input for RAG and CNN` → `1.5.2 A Standard Input for RAG and CNN`
- **Changed:** During Phase 2, ~~each of~~ the two ~~classifiers~~ **modules** had slightly different conceptions of what a request ~~is~~ **is,** and their combination revealed minor differences. One structured input was agreed ~~upon~~ **upon,** which ~~included~~ **includes** the disease, the confidence, the location and the user's question. Both modules ~~are scanned~~ **read a scan** in the same way, so ~~when scanned on any of the two screens it~~ **a scan** returns the same answer ~~when displayed~~ **whether it is viewed on the scan screen or** in the chat.

### 1.5.3 Testing with People Who Know the Field

- **Heading:** `1.5.3 Testing with people who know the field` → `1.5.3 Testing with People Who Know the Field`
- **Changed:** The first field testing was conducted and feedback **was received** from the ~~planters was received,~~ **planters;** their ~~comment~~ **comments** on ~~the~~ usability ~~was~~ **were** positive. It ~~wasn't~~ **was not** a ~~trial; it was~~ **formal trial but** an initial ~~round~~ **round,** and ~~there is~~ no statistics on task ~~completion.~~ **completion were recorded.** A **structured pilot with a** larger group ~~will have a structured pilot that~~ is still ~~on our list. We tested the newly trained CNN, retrained the classifier and created a testing pipeline. It achieved 90 percent accuracy when tested on the validation set and an 80 percent accuracy when tested on new images of leaves that were not included in training or validation. The ten point gap is a valuable, realistic measure: the model is better on images that are similar to its training set than on new images. This is discussed in Section 8.2, and is used to justify the 75% confidence gate.~~ **planned.**

### New section: 1.5.4 Testing the Newly Trained CNN

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> The newly trained CNN was tested: the classifier was retrained and a testing pipeline was created. It achieved 90% accuracy when tested on the validation set and 80% accuracy when tested on new images of leaves that were not included in training or validation. The ten-point gap is a valuable, realistic measure: the model is better on images that are similar to its training set than on new images. This is discussed in Section 8.2, and it is used to justify the 75% confidence gate. A later leak-free five-fold evaluation on the public JMuBEN images, also reported in Section 8.2, measured an accuracy of 97.9%.

### 1.5.5 Streamlining the Integration Flow

- **Heading:** `1.5.5 Streamlining the integration flow` → `1.5.5 Streamlining the Integration Flow`
- **Changed:** The final ~~one~~ **suggestion** was to ~~make everything "flow".~~ **streamline the end-to-end integration flow.** All four modules ~~were~~ **now sit** behind a single backend ~~to~~ **with** which the mobile app ~~communicates~~ **communicates,** and the entire workflow from sign-in to scan, advice, chat and listing was **tested** manually ~~tested~~ and ~~underwent integrated testing. It~~ **through integration tests. Making this happen** took longer ~~to make this happen.~~ than ~~wiring.~~ **the wiring itself.** A shared session was added, which made it possible for the chatbot to see the last scan of the user. Bugs that occurred only when modules ~~call~~ **called** each other were identified and ~~corrected. For example:~~ **corrected, for example** a cache key that ~~didn't~~ **did not** contain the query.

### 1.6 Organisation of the Report

- **Heading:** `1.6 Organization of the Report` → `1.6 Organisation of the Report`
- **Changed:** ~~Chapter 2 presents the~~ **The** problem definition **is presented in Chapter 2,** and ~~Chapter 3 presents~~ the related literature and **the** gaps in ~~it.~~ **it are presented in** Chapter ~~4 outlines the~~ **3. The** requirements of the project, including ~~the project's~~ **its** goals, data and ~~environment.~~ **environment, are outlined in** Chapter ~~5 describes the~~ **4. The** system design **is described in Chapter 5,** and ~~Chapter 6 illustrates~~ the methodology behind each ~~module.~~ **module is explained in Chapter 6.** The implementation is **described** in Chapter 7 ~~using~~ **with** pseudocode, ~~Chapter 8 is~~ the results and ~~discussion,~~ **discussion are presented in Chapter 8,** and the ~~Conclusion~~ **conclusion** and ~~Future Work is~~ **future work are given** in Chapter 9. A glossary, a user manual, **a** test catalogue and **the** team contributions are included in the ~~Appendix.~~ **appendices.**

### PROBLEM STATEMENT

- **Changed:** The growers ~~we are building~~ for **whom PlantIQ is built** are located where four separate problems meet. Each one is well known on its own, but they are usually treated as if they had nothing to do with one another. In the field they all arrive at the same time.

### 2.2 The Gap Between Diagnosis and Action

- **Changed:** Plant-disease classifiers are now common and several are accurate under laboratory conditions. Most of them stop at the label. A farmer told "Leaf Rust, ~~91 percent"~~ **91%"** still has to work out how serious that is, whether the coming weather will make it worse, what to apply and at what concentration. A label with no next step leaves most of the work undone.

### 2.3 Trust and Language in AI Advice

- **Changed:** Large ~~Language Models~~ **language models** write fluent agronomic advice, but fluency is not the same as correctness. A model can state a fungicide dose with full confidence and be wrong, and in farming a wrong dose wastes money, damages the crop or harms the person spraying. An advisory tool for growers therefore has to be tied to a trusted source and has to show when it has stepped outside it.

### 2.4 Limited Market Visibility

- **Changed:** Even a good crop is hard to put in front of ~~buyers.Growers~~ **buyers. Growers** frequently have to rely on middlemen, reducing their cut of the price and their bargaining power. It is difficult to ~~directly~~ contact roasters, ~~traders,~~ **traders** and specialty ~~buyers,~~ **buyers directly,** and many growers never see offers from other buyers.

### 2.5 Formal Problem Statement

- **Changed:** Taking all of these together, the problem ~~we are going to tackle~~ **addressed in this work** is:
- **Changed:** Coffee growers in Karnataka lack a single localised, language-aware platform **on which they can identify a leaf problem, receive advice grounded in trusted sources and current weather, ask follow-up questions in Kannada, and offer their crop directly to buyers.**
- **Removed paragraph:** ~~on which they can identify a leaf problem, receive advice grounded in trusted~~
- **Removed paragraph:** ~~sources and current weather, ask follow-up questions in Kannada, and offer~~
- **Removed paragraph:** ~~their crop directly to buyers.~~

### 2.6 Scope of the Work

- **Changed:** The work reported here covers coffee leaf-disease advice and a direct marketplace. ~~We chose coffee~~ **Coffee was chosen** because the disease set is small enough to cover properly, the region is well defined, and the Central Coffee Research Institute (CCRI) documents ~~give us~~ **provide** an authoritative text source **in which** to ground the ~~advice in.~~ **advice.**

### LITERATURE REVIEW

- **Changed:** ~~In~~ **Seven papers were read in** Phases 1 and ~~2 seven papers were read.~~ **2.** Each ~~will build~~ **covers** a component of what PlantIQ aims to assemble: disease detection, ~~basis-informed~~ **evidence-based** advice, structured knowledge, multimodal models, farmer-facing chat and the role of soil and climate. ~~Summaries~~ **The summaries** are ~~in our own words~~ **paraphrased,** and all figures are those ~~used~~ **reported** by the authors.

### 3.1.1 Abstract

- **Changed:** In this research, an intelligent framework for ~~disease~~ **the** detection and remediation of coffee leaf **diseases** using computer vision and ~~retrieval augmented~~ **retrieval-augmented** generation (RAG) has been proposed. ~~The system use~~ **A** YOLOv8 model **is used by the system** to detect **the** disease ~~from~~ **in** each image of **a** coffee ~~leaves~~ **leaf,** and ~~after that use FAISS model based~~ **FAISS-based** semantic retrieval **is then used** to ~~get the~~ **obtain** information from an agricultural knowledge corpus. The passages are fed into prompts provided to GPT-3.5 to ~~provide~~ **produce** treatment recommendations specific to the disease, based on agricultural references. The proposed approach addresses the ~~behaviour~~ **tendency** of standalone language models to provide unsupported agricultural advice. The experimental results show that visual disease recognition with knowledge-grounded advisory generation can achieve about 12% accuracy improvement over a language-model-only baseline and reduce the number of hallucinated statements by 30%, indicating the effectiveness of the combination.

### 3.1.2 Research Gap

- **Changed:** Traditional disease detection systems primarily aim to diagnose diseases, but do not offer useful recommendations for treatment. Current methods fail to consider factors such as real-time environmental ~~factors,~~ **conditions,** chemical dose verification and regional language accessibility when providing generated advice, even though RAG enhances the factual basis of the advice. Additionally, ~~no integration of the~~ **a platform that integrates** disease ~~diagnosis –~~ **diagnosis,** personalised agricultural recommendations ~~–~~ **and** direct market access ~~platform~~ has **not** been investigated.

### 3.1.3 Advantages

- **Heading:** `3.1.3 Positives` → `3.1.3 Advantages`
- **Changed:** The proposed framework is able to seamlessly combine visual disease detection with knowledge-based advisory generation, mitigating the reliance on **unsupported** language-model ~~answers without support.~~ **answers.** The semantic retrieval with FAISS enhances the contextual relevance of treatment recommendations, and the modular design enables independent enhancements in detection and generation. The 12% accuracy boost and 30% decrease in hallucinations highlight the promise of RAG in creating more accurate agricultural advisory services.

### 3.1.4 Disadvantages

- **Heading:** `3.1.4 Drawbacks` → `3.1.4 Disadvantages`
- **Changed:** The system does not include real-time weather data ~~including~~ **such as** humidity, precipitation and temperature in the treatment recommendation. It also does not include specific reference to the doses and amounts of pesticides and chemicals ~~used~~ **given** in official agricultural texts. Moreover, the lack of regional-language support and direct marketplace integration reduces its usability and accessibility as a comprehensive farmer-support platform.

### 3.2.1 Abstract

- **Changed:** To enhance information retrieval and explainability, Zhao et al. ~~presents~~ **present** an agricultural advisory framework that integrates large language models (LLMs) with structured knowledge graphs. The system builds a Neo4j ~~Knowledge~~ **knowledge** graph of the relationships between crop, pathogen, soil ~~condition,~~ **condition** and disease symptom. The extracted structural representation is ~~for~~ **processed by** GraphSAGE and Graph Attention Networks, and the textual information is processed by a BERT-based encoder. To produce contextually relevant answers from agricultural subgraphs, these representations are coupled with GPT-Neo. The framework achieves about 94% precision and 92% recall, showing the ~~good~~ **strong** performance of the combination of structured agricultural relations and language generation. The approach also makes the results more interpretable by allowing the exploration of the relationships between symptoms, diseases and treatments via the knowledge graph.

### 3.2.2 Research Gap

- **Changed:** Traditional systems for document retrieval often have difficulty capturing complex relationships among the various factors involved in the agricultural context, including soil properties, disease symptoms, crop ~~varieties,~~ **varieties** and treatments. Knowledge graphs overcome this by being structured and ~~using~~ **supporting** reasoning, but they require a lot of **domain** expertise ~~in the domain~~ and computing power to build and maintain. ~~There~~ **Further research** is ~~a need to develop the research further,~~ **needed** to incorporate graph-based reasoning into real-time disease detection, environmental monitoring and **region-specific** agricultural ~~advice for regions.~~ **advice.**

### 3.2.3 Advantages

- **Heading:** `3.2.3 Positives` → `3.2.3 Advantages`
- **Changed:** The proposed framework offers a structured representation of agricultural knowledge to enable more explainable and contextually appropriate recommendations. It can perform reasoning on interrelated agricultural entities with the help of the combination of GraphSAGE, Graph Attention Networks, ~~BERT,~~ **BERT** and GPT-Neo. The reported 94% precision and 92% recall are good results, and ~~they are~~ **the framework is** able to extract the links between symptoms and treatments, which is more transparent than traditional text-based retrieval methods.

### 3.2.4 Disadvantages

- **Heading:** `3.2.4 Drawbacks` → `3.2.4 Disadvantages`
- **Changed:** Extensive data preparation, domain ~~knowledge,~~ **knowledge** and computational resources are needed to develop and maintain a comprehensive agricultural knowledge graph. The architecture adds to the complexity of traditional semantic retrieval ~~systems,~~ **systems** and may need regular updates as agricultural knowledge continues to develop. Moreover, the proposed framework is not ~~particularly~~ designed **specifically** for coffee growing in Karnataka and lacks integration of image-based disease diagnosis, real-time weather data and direct coffee marketplace functionality.

### 3.3.1 Abstract

- **Changed:** The aim of this research is to implement Convolutional Neural Networks (CNNs) for **the** automatic classification of **diseased** coffee ~~leaves with diseases.~~ **leaves.** This research employs around ~~8500~~ **8,500** images depicting coffee leaf rust, Cercospora and leaf miner conditions. To increase the training diversity, image augmentation methods are used, and a CNN ~~network,~~ similar to ~~that used in~~ GoogLeNet is trained using the Adam optimiser and a cross-entropy loss function. The network automatically extracts visual features related to disease symptoms, ~~alleviating~~ **reducing the** reliance on manually designed image descriptors. ~~Results of experiments~~ **The experimental results** show ~~that the~~ **a** classification accuracy ~~is at~~ **of** about 90%, which is better than the Support Vector Machine and **the** smaller neural network baselines that were evaluated. The results ~~have been able to~~ confirm the efficiency of deep convolutional networks ~~to detect the~~ **in detecting** common coffee leaf ~~disease using~~ **diseases through** image analysis.

### 3.3.2 Research Gap

- **Changed:** Coffee disease diagnosis is usually done ~~manually, requiring~~ **manually and requires** agricultural skills, which can ~~be a delay.~~ **cause delays.** CNN-based systems automate this process, but they are not necessarily able to cope with uncontrolled field images with variations in lighting, background, leaf orientation and disease severity. Further, ~~the~~ classification-based approaches tend to focus on the classification ~~and~~ **alone,** do not incorporate any **confidence-based** decision-making ~~process related to confidence~~ and do not relate disease predictions to treatment options or **to an** assessment of environmental risk.

### 3.3.3 Advantages

- **Heading:** `3.3.3 Positives` → `3.3.3 Advantages`
- **Changed:** The proposed CNN shows a good classification capability, with a mean accuracy of about 90% ~~in~~ **across** three classes of coffee leaf diseases. ~~Enhancing images with the~~ **Image** augmentation ~~technique~~ increases the diversity of **the** training **data,** and automatic feature extraction saves ~~in~~ manual image processing. Its ~~effectiveness outcompared~~ **better performance compared** with ~~the~~ standard machine-learning models validates CNNs as a worthwhile tool for automatic coffee disease recognition and ~~in~~ **for** broader agricultural applications.
- **Removed paragraph:** ~~3.3.4 Drawbacks The model only covers 3 type of disease, which means that other common disease conditions in coffee leaves can't be covered. The reported results are not sufficiently robust in terms of performance on uncontrolled field photographs to be certain of its reliability in the real world. Moreover, the system does not have any rejection mechanism for the uncertain prediction, uncertain environment, and generation of the treatment advices, respectively, which is required for the system functions beyond disease classification.~~

### New section: 3.3.4 Disadvantages

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> The model covers only three types of disease, which means that other common conditions of coffee leaves are not covered. The reported results are not sufficiently robust in terms of performance on uncontrolled field photographs to be certain of their reliability in the real world. Moreover, the system has no mechanism for rejecting uncertain predictions, no environmental context and no generation of treatment advice, all of which are required for a system that goes beyond disease classification.

### 3.4.1 Abstract

- **Changed:** ~~Sapkota and co-authors conducted a~~ **A** thorough review of over 200 research papers on the use of large language models in ~~agriculture.~~ **agriculture was conducted by Sapkota and co-authors. The study compares model families such as GPT-4, Gemini, LLaMA, PaLM and DeepSeek, as well as approaches such as vision-language integration, chain-of-thought prompting and retrieval-augmented generation. Special focus is given to the integration of agricultural imagery, textual information and environmental measurements for better decision-making. The examined results show that multimodal retrieval-based methods can increase the accuracy by about 10-25% compared with single-modal retrieval-based methods in the tested scenarios. The authors also point out the significant computational needs of training large models from scratch and propose pretrained architectures with targeted fine-tuning as a more practical way to develop such systems.**
- **Removed paragraph:** ~~The study Compares model families such as GPT-4, Gemini, LLaMA, PaLM, and DeepSeek, as well as approaches like vision-language integration, chain-of-thought prompting, and retrieval-augmented generation. Special focus is given to the integration of agricultural imagery, textual information and environmental measurements for better decision making. The examined result show that the multimodal retrieval-based methods are able to increase the accuracy by about 10-25% compared to the single-modal retrieval based methods in the tested scenarios. The authors also point out the significant computational needs for training large models from scratch and propose to use pretrained architectures with background fine-tuning as a more practical way to develop.~~

### 3.4.2 Research Gap

- **Changed:** Existing agricultural AI systems usually ~~take~~ **process** visual, textual and environmental data separately, which prevents them from making comprehensive recommendations. While multimodal models provide more context, there are still issues with computation speed, model accuracy, data ~~integration,~~ **integration** and deployment in low-resource settings. There remains a lack of adequate ~~evidence,~~ **evidence** in ~~literature,~~ **the literature** of the ~~synergistic~~ integration of ~~a~~ multimodal disease ~~diagnosis,~~ **diagnosis** with ~~a~~ verified advisory generation and **a** farmer-oriented ~~service,~~ **service** in a region-specific agricultural system.

### 3.4.3 Advantages

- **Heading:** `3.4.3 Positives` → `3.4.3 Advantages`
- **Changed:** The review covers the research on agricultural language models in ~~depth,~~ **depth** and ~~emphasizes~~ **emphasises** the benefits of using multiple information modalities. Multimodal retrieval approaches show ~~promise of~~ **promising** improvements in ~~accuracy~~ **accuracy,** reported as around 10-25%. The research also ~~reveals~~ **shows** that pretrained models, targeted ~~fine-tuning,~~ **fine-tuning** and retrieval augmentation are viable approaches to ~~mitigate~~ **reduce** computational ~~expenses~~ **expense** and enhance the contextual relevance of agricultural AI models.

### 3.4.4 Disadvantages

- **Heading:** `3.4.4 Drawbacks` → `3.4.4 Disadvantages`
- **Changed:** The study is a literature review ~~which~~ **and** does not ~~show~~ **present** an end-to-end agricultural advisory platform ~~that~~ **developed by** the ~~researcher developed independently. There are a number of reasons why the~~ **authors. The** reported performance gains ~~are found to~~ come from different research contexts, so direct comparison is ~~hard to make.~~ **difficult.** Furthermore, multimodal systems ~~have~~ **face** computational, data alignment, network dependency and deployment challenges. A review ~~does not stand on its own as a validation of a~~ **cannot by itself validate** disease detection, multilingual interaction and marketplace ~~integration,~~ **integration** specific to the state of Karnataka.

### 3.5.1 Abstract

- **Changed:** ~~Chat~~ **Farmer.Chat** is a conversational agricultural advisory platform **designed** to increase **the** accessibility of farming information for smallholder farmers. It works on ~~the apps that are~~ widely used ~~by people, like~~ **apps such as** WhatsApp and Telegram, ~~and it does~~ **so users do** not ~~require users~~ **have** to ~~get to grips with~~ **learn** anything complicated. It ~~utilizes~~ **utilises** ElasticSearch ~~Document Retrieval~~ **document retrieval and BERT embeddings** to locate relevant ~~information pertaining to Agriculture and BERT embedding to locate the relevant~~ **agricultural** information, and uses a fine-tuned GPT-based language model to generate a conversational response. The authors ~~claim to serve~~ **report serving** over ~~15 000~~ **15,000** farmers and ~~process~~ **processing** about ~~300 000~~ **300,000** queries. About 75% of the advice ~~received~~ was judged **accurate** by ~~agronomists to be accurate,~~ **agronomists,** and farmers' comments focused on the positive aspects of conversational engagement and language flexibility. The study provides a glimpse into the viability and potential of ~~the use of~~ agricultural chatbots that are accessible and ~~easily retrievable.~~ **easy to use.**

### 3.5.2 Research Gap

- **Changed:** Knowledge about agriculture is frequently spread over technical literature and institutional sources ~~which~~ **that** are not easily accessible to ~~farmers in~~ small-scale ~~agriculture. Farmer.To resolve~~ **farmers. Farmer.Chat addresses** this problem of ~~accessibility, the Chat uses~~ **accessibility by using** familiar messaging systems and natural-language interaction. ~~But,~~ **However,** current conversational advisory systems are not yet capable of combining image-based disease diagnosis, **location-specific** environmental data ~~from the specific location~~ and domain-specific knowledge about coffee cultivation. The link between agricultural advisory services and direct involvement in markets is also weak.

### 3.5.3 Advantages

- **Heading:** `3.5.3 Positives` → `3.5.3 Advantages`
- **Changed:** The platform is designed to be accessible and ~~designed~~ to interact ~~in a conversational way~~ **conversationally** through popular messaging apps. Its retrieval-based architecture helps to deliver relevant agricultural ~~information~~ **information,** and its language flexibility makes it more ~~user friendly among~~ **user-friendly for** a variety of farming communities. ~~Reported~~ **The reported** adoption by more than 15,000 farmers and some 300,000 queries ~~indicate~~ **indicates** that the application is effective. Evaluation ~~from~~ **by** agronomists is also helpful in assessing the reliability of ~~recommendations generated.~~ **the generated recommendations.**

### 3.5.4 Disadvantages

- **Heading:** `3.5.4 Drawbacks` → `3.5.4 Disadvantages`
- **Changed:** ~~Currently, about~~ **About** 75% of the **generated** advice ~~generated~~ is deemed accurate, ~~but~~ **so** there is room for improvement in the reliability and verification of the advice. ~~It~~ **The platform** lacks integrated ~~image based~~ **image-based** coffee disease detection and a knowledge base targeting coffee diseases in the ~~state~~ **coffee-growing regions** of ~~Karnataka coffee-growing regions.~~ **Karnataka.** Besides that, the framework ~~doesn't~~ **does not** include explicit chemical dosage validation, live microclimate ~~integration, and~~ **integration or** direct farmer-to-buyer marketplace functionality, ~~limiting~~ **which limits** it to conversational agricultural assistance.

### 3.6.1 Abstract

- **Changed:** Santhosha and Umesh examine the use of ensemble machine-learning algorithms to predict coffee yield ~~for the given~~ **from** soil ~~data~~ and agricultural data. The study uses about ~~19000~~ **19,000** soil records collected from **the** Central Coffee Research Institute (CCRI), Karnataka, to study the relation between soil characteristics and coffee productivity. The **predictive** performance of ~~some of the~~ supervised learning ~~algorithms,~~ **algorithms** such as Random Forest, Decision Tree, Gradient Boosting and Extra Trees ~~are compared in terms of their predictive performance.~~ **is compared.** According to **the** experimental results, Random Forest and Extra Trees perform ~~best (with~~ **best, with** results of **about** 91% being ~~reported).~~ **reported.** The research also shows that ~~there are significant differences in~~ the yield of coffee ~~when there is just~~ **differs significantly with even** a slight change in ~~the~~ soil chemistry. The findings show the potential of ensemble learning to predict agricultural productivity and **to** plan cultivation based on data.

### 3.6.2 Research Gap

- **Changed:** The productivity of ~~the~~ coffee is related to a number of interacting ~~factors~~ **factors,** including soil composition, nutrient availability, environmental factors and disease incidence. Yield estimation methods used in traditional agriculture are not necessarily able to ~~measure~~ **capture** the nonlinear ~~relationship~~ **relationships** between these parameters. Ensemble models are useful in improving ~~soil based~~ **soil-based** yield prediction, but are not directly useful for disease identification, treatment recommendations or real-time environmental advisory requirements. There is still great potential to integrate soil-based predictive information ~~with the~~ **into** larger systems of agricultural intelligence.

### 3.6.3 Advantages

- **Heading:** `3.6.3 Positives` → `3.6.3 Advantages`
- **Changed:** The study is based on a large database of ~~~19,000~~ **about 19,000** soil records linked to CCRI, which can provide relevant information for coffee cultivation in Karnataka. By comparing several machine learning algorithms, ~~you can identify~~ **the study identifies** which algorithms are effective for ~~predicting the results, and the performance of~~ **prediction, with** Random Forest and Extra Trees ~~is~~ **performing at** around 91%. The study shows the importance of soil chemistry in coffee productivity and provides a basis for the inclusion of soil-health analysis in ~~the~~ agricultural decision-support ~~system.~~ **systems.**

### 3.6.4 Disadvantages

- **Heading:** `3.6.4 Drawbacks` → `3.6.4 Disadvantages`
- **Changed:** The research is mainly on predicting yields and not **on** the diagnosis of disease or **the** recommendation of treatment. The predictive performance relies on the quality and representativeness of the soil ~~records~~ **records,** and the approach described ~~here~~ does not ~~create continuous integration of~~ **continuously integrate** live environmental measurements. Moreover, the system lacks the ability to ~~recognize the~~ **recognise** disease from images, to provide advisory services through ~~conversation,~~ **conversation** and to ~~directly contain a functionality of the~~ **offer any** agricultural ~~market,~~ **market functionality,** providing only the capacity to estimate ~~the~~ productivity.

### 3.7.1 Abstract

- **Changed:** Patil et al. explore the effect of elevation and rainfall on coffee plant attributes with a study of cultivation plots in **the** Chikmagalur and Hassan districts of Karnataka. Measurable plant characteristics such as leaf area, leaf weight, node ~~density,~~ **density** and bean-related characteristics were explored to find relationships between environmental factors and coffee development. ~~A~~ **Statistical analysis reports a** significant positive correlation between specific leaf area and elevation ~~has been reported~~ (r = **0.912). There is a moderate correlation of r = 0.475 between rainfall and bean defects. These results show that the physiological and crop responses of the coffee plant change measurably with differences in local environmental conditions, emphasising the need to consider geographical and climatic context in agricultural research and advisory development.**
- **Removed paragraph:** ~~0.912) by statistical analysis. There is a medium correlation of r = 0.475 between the two variables of rainfall and bean defects. These results show that the physiological and crop responses of the coffee plant can change in ways that are measurable because of differences in the local environmental conditions, emphasizing the need to consider geographical and climatic context in agricultural research and advisory development.~~

### 3.7.2 Research Gap

- **Changed:** Agricultural advisory systems often give generic advice, ~~while~~ neglecting local differences in elevation, ~~rainfall,~~ **rainfall** and microclimate. The study ~~defines~~ **establishes** statistical relationships between the environment and coffee ~~characteristics~~ **characteristics,** but the results are not converted ~~to~~ **into** an automated ~~decision support~~ **decision-support** tool. ~~The use of~~ **Combining** environmental information from mobile sources ~~combined~~ with ~~the~~ **disease** recognition ~~of disease~~ and **treatment** recommendations ~~for treatment~~ is an interesting area for research, offering the prospect of ~~building~~ **more context-aware** agricultural advisory ~~systems that are more context-aware.~~ **systems.**

### 3.7.3 Advantages

- **Heading:** `3.7.3 Positives` → `3.7.3 Advantages`
- **Changed:** The findings of this research are geographically relevant to ~~the~~ coffee cultivation ~~of Karnataka~~ **in Karnataka,** as ~~it~~ **the study** uses field-based data from two districts, Chikmagalur and Hassan. The high ~~level of~~ correlation between elevation and specific leaf area (r = 0.912) and the moderate ~~level of~~ correlation between rainfall and bean defects (r = 0.475) ~~is an indicator of~~ **indicate** the importance of local adaptation. **The results offer empirical evidence of the need to integrate location and weather data into agricultural monitoring and advisory services.**
- **Removed paragraph:** ~~The results offer empirical evidence on the need to integrate location and weather data in agricultural monitoring and advisory services.~~

### 3.7.4 Disadvantages

- **Heading:** `3.7.4 Drawbacks` → `3.7.4 Disadvantages`
- **Changed:** The study does not focus on the development of an operational agricultural decision-support system, but rather on statistical relationships. Correlation does not prove causation, and results from the **surveyed** areas ~~surveyed~~ might need to be validated in other growing areas. Moreover, the research ~~doesn't~~ **does not** include automation for disease detection, real-time environmental monitoring, recommendation ~~generation,~~ **generation** or interaction with farmers in multiple languages, which restricts its immediate use ~~for~~ **in** an integrated agricultural advisory system.

### 3.8 Summary of the Literature Surveyed

- **Heading:** `3.1 Summary of the Survey` → `3.8 Summary of the Literature Surveyed`
- **Added paragraph:** The main idea of each surveyed paper, the inference drawn from it and what it leaves open are summarised in Table 3.1.

### 3.9 Research Gap

- **Heading:** `3.2 Overall Research Results:` → `3.9 Research Gap`
- **Changed:** ~~The use of all of the ingredients~~ **Every ingredient used** in PlantIQ is supported by **the** literature. ~~Coffee leaves are classified by CNNs,~~ **CNNs classify coffee leaves,** retrieval cuts down invented advice, chatbots reach ~~out to~~ smallholders ~~by~~ **through** messaging ~~apps~~ **apps,** and climate ~~obviously~~ **clearly** affects the ~~behavior~~ **behaviour** of coffee plants. ~~So we couldn't find anything~~ **However, no work was found** that ~~could combine~~ **combines** all **of** these for the coffee growers of ~~Karnataka. It's here that~~ **Karnataka, and this is where** the ~~spaces remain vacant. Label is right down~~ **gaps remain. Diagnosis stops at the label: existing detectors name the disease but do not tie it** to the ~~diagnosis. There are already detectors which tell the disease. They never tie into the humidity/temperature here~~ **local humidity** and ~~nor do they~~ **temperature or** provide a ~~wise remedy—and it's~~ **suitable remedy, which is** left to the ~~reader! There are no verification~~ **reader. Advice is not verified: retrieval reduces hallucination, but none** of ~~advices. No system we~~ **the** identified ~~analyzed~~ **systems checks** the numbers ~~on their~~ **in its** own ~~in their response,~~ **response. A simple** and ~~retrieval minimizes hallucination. If you must perform the test right and do it wrong if you don't, then a simple test that is good to have as a~~ **useful** safety measure is to ~~see if any of~~ **check whether each chemical dose in** the ~~chemical doses are mentioned~~ **answer appears** in the source ~~text. None~~ **text, and none** of the **examined** works ~~that were examined do~~ **does** this. ~~Language assistance is available, but limited. Most of the agricultural AI tools accept English text. Farmer.It's a text channel for all questions except one, Chat. For instance, there was no chain of coffee language, from voice to voice in the kannada script, with the grower's own scan as background. Very few regions are specific. The retrieval systems provided cover general retrieval systems or other crops and areas. None is based on the CCRI documents, the disease set of the state of Karnataka or Arabica estates at altitude. Markets are in a different world. Agricultural marketplaces are present but there is no linkage between these and agricultural advisory tools. If the grower has just suffered a leaf problem and wants to sell, they will need to change app and contacts. The term of "field readiness" is seldom discussed. There have been many papers claiming their accuracy with a curated set of tests and very little discussion of things like response time, repeat requests, failed third party APIs, security, and so on. The tool that gives the user spray advice and user accounts is more important than accuracy. Everything can be done in the PlantIQ pipeline: take a picture of a leaf, get grounded advice based on the weather, talk in your own words and then list your crop and sell it in one app.~~
- **Added paragraph:** Language support is available but limited. Most agricultural AI tools accept only English text, and Farmer.Chat is the main exception. No system offered a coffee-specific chain from voice input to a reply in Kannada script with the grower's own scan as context. Regional focus is rare: the retrieval systems cover general content or other crops and areas, and none is based on the CCRI documents, the disease set of Karnataka or Arabica estates at altitude. Markets are disconnected: agricultural marketplaces exist, but they are not linked to advisory tools, so a grower who has just dealt with a leaf problem and wants to sell has to change apps and contacts. Field readiness is seldom discussed: many papers report accuracy on a curated test set with very little discussion of response time, repeat requests, failing third-party APIs or security, which matter as much as accuracy in a tool that gives spray advice and holds user accounts. The PlantIQ pipeline covers all of these in one app: a leaf is photographed, grounded advice based on the weather is received, follow-up questions are asked in the grower's own words, and the crop is listed for sale.

### 4.1 Purpose and Scope

- **Changed:** This chapter ~~is a list of~~ **sets out** what **PlantIQ** is expected to ~~happen and when to expect it at PlantIQ.~~ **do.** It includes the aims, **the** functional and non-functional requirements, the data on which the system relies, the working environment and whether each aim ~~is~~ **was** achieved ~~at~~ **by** the end of Phase 3. The product ~~will be~~ **is** a mobile and web application for the coffee growers and buyers of ~~Karnataka with~~ **Karnataka, backed by** a single server application.

### 4.2.1 Primary Objectives

- **Heading:** `4.2.1 Primary objectives` → `4.2.1 Primary Objectives`
- **Changed:** ~~1.~~ Train and deploy a ResNet-50 classifier to recognise the main coffee leaf conditions in farmer-taken ~~photos and,~~ **photos, and** make an explicit decision when the model is not sure.
- **Changed:** ~~2.~~ Construct a retrieval-augmented advisory system that ~~can respond to~~ **answers** questions based on authoritative **coffee** research ~~coffee text,~~ **text and** current weather information, and ~~check~~ **checks the** dosages ~~referred to.~~ **it mentions.**
- **Changed:** ~~3.~~ Provide a chatbot ~~which~~ **that** can ~~hear~~ **take voice** and ~~speak~~ **text input** in Kannada and English, recall the previous conversation and ~~be able to~~ access the grower's recent scan.
- **Changed:** ~~4.~~ Implement a direct grower-to-buyer platform, including one-tap contact and navigation, and proximity sorting.

### 4.2.2 Secondary Objectives

- **Heading:** `4.2.2 Secondary objectives` → `4.2.2 Secondary Objectives`
- **Changed:** ~~1.~~ Use real microclimate data ~~for~~ **in** Phase ~~2~~ **3** instead of the simulated ~~data.~~ **data of Phase 2.**
- **Changed:** ~~2.~~ Embed the four modules behind clean interfaces with one flow from image through advisory to marketplace.
- **Changed:** ~~3.~~ Include automated tests for each module, **the** integrated application and basic security, to detect regressions early.
- **Changed:** ~~4.~~ Provide ~~fall-backs to~~ **fallbacks for** the language model and speech recognition ~~if~~ **when** external services are **not available, in order to keep the system usable.**
- **Changed:** ~~not available, in order to keep the system usable.~~ **Use open data, open-source frameworks and published models where these are available.**
- **Removed paragraph:** ~~5. Use open data, open source frameworks and published models if these are available.~~

### 4.3 Functional Requirements

- **Changed:** Table 4.1 ~~shows~~ **lists** the functional ~~requirement~~ **requirements** of the system, which ~~includes~~ **include** user authentication, disease detection, advisory support, multilingual interaction and **the** management of crop ~~listing.~~ **listings.** These requirements specify the essential functions that the system must ~~possess.~~ **provide.**

### 4.4 Non-Functional Requirements

- **Added paragraph:** The non-functional requirements and their targets are listed in Table 4.2.

### 4.5.1 Leaf Images

- **Heading:** `4.5.1 Leaf images` → `4.5.1 Leaf Images`
- **Changed:** In Phase 2, three public datasets were combined into a composite dataset from which the classifier is derived. JMuBEN is ~~a set of~~ **an** Arabica-specific coffee ~~for use against~~ **leaf set covering** rust, leaf miner and ~~cercospora.~~ **Cercospora. PlantVillage provides numerous photos of single leaves and helps where the coffee-specific set is limited. PlantDoc adds low-quality field photographs with uneven lighting and background noise, which help to close the gap between photos taken in a laboratory and what a grower would take on an estate. The Phase 3 model recognises five conditions; Phoma Blight was not in the Phase 2 target list.**
- **Changed:** ~~PlantVillage provides numerous photos of single leaves and assists in areas where the coffee-specific set is limited. PlantDoc also introduces low-quality photography from the field, with uneven lighting and background noise, and its task is to close the difference between the photos taken in the lab and what a grower would take on an estate. There are 5 conditions recognised in the Model–Phase 3. Phoma Blight was not in the Phase 2 target list. There are two~~ **Two** sets of evaluations ~~in this report.~~ **were reported for Phase 3.** Images ~~used~~ in the validation set ~~are~~ **come** from the same distribution as **the** training ~~data.~~ **data, while the "new leaf" set contains leaves that the model has never seen in any form and is a more honest indicator of behaviour on a new picture. A third, leak-free evaluation was added later, because an audit found that the 58,549 JMuBEN files come from only 861 distinct leaf patches; in this evaluation every copy of a patch stays on the same side of each fold.**
- **Changed:** The ~~"new leaf" set has leaves that the model has never photographed or viewed in any form and is a more honest indicator of behaviour on a new picture. Automated Tests are~~ **fast automated tests do** not ~~conducted with~~ **use** real images. The pytest suite uses Pillow to create synthetic and intentionally broken images to keep the tests fast and repeatable, ~~but~~ not to test diagnostic ~~accuracy~~ **accuracy. Four separate real-model tests load the deployed weights and classify one sample photograph** of ~~the image.~~ **each class.**

### 4.5.2 Advisory Knowledge Base

- **Heading:** `4.5.2 Advisory knowledge base` → `4.5.2 Advisory Knowledge Base`
- **Changed:** The advisory engine responds ~~to~~ **from** the CCRI text, which contains information ~~relating to~~ **on the** identification, treatment and management of coffee diseases in Karnataka from the Central Coffee Research ~~Institute.~~ **Institute, together with research articles on coffee diseases, pests and nutrition (14 PDF documents and 931 passages in all).** The documents are broken up into passages and indexed twice, allowing a passage to be located by its meaning as well as by its exact wording. The dense index is a FAISS index of ~~768-dimensional~~ **1024-dimensional bge-m3 embeddings (768-dimensional** BGE-base-en ~~embeddings;~~ **embeddings when no GPU is available);** the sparse index is a BM25 keyword index over the same passages. Each passage carries a ~~disease~~ **topic** tag, which lets the pipeline ~~filter~~ **prefer** retrieved text ~~to~~ **on** the disease **that** the classifier has named.

### 4.5.3 Live Weather

- **Heading:** `4.5.3 Live weather` → `4.5.3 Live Weather`
- **Changed:** In Phase 2, weather and elevation were simulated, followed by NASA POWER and Open Elevation. In Phase 3 the weather ~~was added as~~ **is fetched from Open-Meteo, which provides the temperature, humidity, rainfall, elevation and** a ~~coordinate from Open-Meteo where it provided temperature, humidity and rainfall~~ **three-day forecast** for a given coordinate. If the app is not able to get **a** GPS fix, no default ~~/~~ **or** invented reading is ~~given. The~~ **used; the** advisory is **still** issued, ~~even if the weather isn't affecting the discussion.~~ **but without weather.** This is ~~what can be~~ called ~~as~~ the zero-mock ~~policy~~ **policy,** and it is ~~tested~~ **checked** by ~~a~~ **an automated** test.

### 4.5.4 Application Data

- **Heading:** `4.5.4 Application data` → `4.5.4 Application Data`
- **Changed:** All the data written by the application is stored in a relational ~~store, via~~ **database (PostgreSQL, or SQLite for zero-configuration deployments) through** SQLAlchemy: user accounts, cached scan ~~data,~~ **results,** marketplace listings ~~(with photo galleries~~ **and chats. Listing photos and chat images are** stored as ~~JSON),~~ **sanitised image files, with their captions** and ~~chats (with leaf images stored as Base64~~ **paths in the database,** so **that** they ~~can be refreshed~~ **survive page refreshes** without ~~losing data).~~ **bloating the database rows.** Using an ORM keeps the data layer independent of the particular database engine during development and testing. **The data assets are summarised in Table 4.3.**

### 4.6 Software and Hardware Environment

- **Changed:** ~~This is for development~~ **Development** and testing ~~purposes~~ **were carried out** on a Windows 11 laptop with **an** NVIDIA RTX **3070 Laptop** GPU (CUDA 12) and Python 3.11. The server is ~~one~~ **a** single FastAPI application on top of a relational database. The client is a **React** web app wrapped for Android using Capacitor 7, so it ~~will be~~ **runs as** a ~~PWA~~ **web app** in a browser or ~~PWA~~ as an installed app. Language-model calls are first sent to Gemini and then **to** Groq. A CPU fallback is available for the GPU parts, but the numbers in this report ~~are based~~ **were measured** on the GPU laptop.

### 4.7 Constraints and Assumptions

- **Changed:** ~~•~~ The free Gemini tier allows only about 20 requests a day, so the system cannot depend on it alone.
- **Changed:** ~~• Currently there~~ **There** is **currently** no support for ~~use without~~ **offline use, so diagnosis requires** a connection to the ~~back end so diagnosis must require a connection to the back end. Currently, weather~~ **backend. Weather** data is available only at grid ~~level~~ **level,** and soil data ~~and elevation are~~ **is** not included.
- **Changed:** ~~•~~ The marketplace ~~is~~ **does** not ~~responsible for contract and payment.~~ **handle contracts or payments.**
- **Changed:** ~~•~~ The Kannada **word** error rate ~~could~~ **was** not ~~be calculated because~~ **measured in this work;** the figure ~~(12.4%) has been~~ **of 12.4% is the** published **value** for the local speech model.

### 4.8 Status of the Objectives

- **Changed:** ~~Language targets note: Requirements for~~ **The status of each objective at the end of** Phase ~~2 was to get at least 70 percent word accuracy~~ **3, and the section of this report** in ~~Kannada agricultural speech. The word error rate of 12.4% obtained from our work~~ **which it** is ~~the published word error rate for the local Kannada model. It has not been measured from farmers' recordings .It was not measured it on farmers' recordings, and this has been highlighted~~ **discussed, are given** in ~~the limitations.~~ **Table 4.4.**
- **Added paragraph:** Language targets note: The Phase 2 requirement was at least 70% word accuracy on Kannada agricultural speech. The word error rate of 12.4% quoted in this work is the published word error rate of the local Kannada model. It has not been measured on farmers' recordings, and this is highlighted in the limitations.

### 5.1 Architectural Overview

- **Changed:** The plan in Phase 2 was to deploy a set of services individually behind a gateway. During ~~the course of~~ integration, the four modules were ~~integrated~~ **combined** into a single backend ~~application, sharing~~ **application that shares** authentication, ~~and they shared~~ a database session and a common request format. This gave up the **planned** independent scaling ~~that was planned on for~~ **in favour of** simplicity, which was appropriate for this project, **with** one deployment ~~target,~~ **target** and a short integration window.

### 5.2 The Four Layers

- **Changed:** Table 5.1 elaborates on the four primary layers of the ~~systems: User Inputs, Perception~~ **system: client** and **inputs, perception and processing, AI reasoning and advisory, and storage and outcomes. It summarises the main components in each layer and the function of each layer in the overall flow of the system.**
- **Removed paragraph:** ~~Processing, AI Reasoning and Advisory, and Storage and Outcomes. It provides a summary of the main features in each layer and a description of the function of each layer in the overall flow of the system.~~

### 5.3 Request Flow

- **Changed:** ~~There are 9 steps in the~~ **The** main flow for **a** grower ~~who has~~ **with** a sick leaf ~~image.~~ **has nine steps.**
- **Changed:** ~~1. The grower enters his/her name and signs in or uploads~~ **After signing in,** a leaf ~~photograph.~~ **photograph is uploaded by the grower.** If location is ~~enabled~~ **enabled,** the app ~~will~~ also ~~include~~ **sends** the GPS coordinates of the estate.
- **Changed:** ~~2. Classifier verifies a~~ **The SHA-256** cache ~~for SHA-256.~~ **is checked by the classifier.** On a miss it runs the ResNet-50 forward pass and returns a class, a confidence and the full probability distribution.
- **Changed:** ~~3.~~ The microclimate service ~~receives~~ **fetches** the temperature, humidity and rainfall ~~data from Open-Meteo at~~ **for** the same coordinates **from Open-Meteo** and calculates a **rule-based** disease-favourability ~~score based on the rules.~~ **score.**
- **Changed:** ~~4.~~ The disease label, the confidence and the weather summary are ~~added~~ **passed** to the retrieval pipeline. Dense and keyword search each return their top ~~15~~ **20** passages, which are fused, ~~filtered to~~ **reranked with a preference for** the **diagnosed** disease and ~~reranked down~~ **reduced** to the top 3.
- **Changed:** ~~5.~~ These passages, the disease and the weather are combined into a prompt. ~~Responds with~~ **The answer is generated by** Gemini, and ~~Grok will respond~~ **Groq is used as a fallback** if Gemini is unavailable.
- **Changed:** ~~6.~~ After the ~~text~~ **answer** is ~~retrieved,~~ **generated,** the dosage audit checks each dose in ~~the answer with~~ **it against** the retrieved ~~text,~~ **text** and marks ~~it~~ **the advisory** as Verified or ~~Caution at the advisory column.~~ **Caution.**
- **Changed:** ~~7. This~~ **The** result is presented to the grower and saved to the database, ~~allowing~~ **so that** the chatbot ~~to~~ **can** continue **from** the ~~scan's process.~~ **scan.**
- **Changed:** ~~8.~~ When the grower asks ~~for~~ a follow-up ~~via speech~~ **question** in ~~Kannada,~~ **Kannada by speech,** the speech chain converts the speech to ~~script,~~ **text,** the ~~pre-router recognizes~~ **language router recognises** the **Kannada** script and ~~creates a query in~~ **writes an** English ~~for the search,~~ **search question,** and the answer comes back in Kannada script.
- **Changed:** ~~9.~~ Once the crop is ready, the grower ~~is responsible for making~~ **creates** a listing. ~~Viewings~~ **Listings** are sorted by ~~distance~~ **distance,** and ~~in one tap~~ buyers can open ~~up to~~ Maps, call or start a WhatsApp ~~chat.~~ **chat in one tap.**
- **Changed:** Context is ~~stored~~ **carried** along with the data in the links between layers. The grower can ask the chatbot a question such as ~~"will~~ **"Will** it get ~~worse?,"~~ **worse?",** and it ~~will respond with~~ **responds using** the scan result, **the** live weather, **the** last 8 chat turns and **the** retrieved ~~passages~~ **passages,** without the grower repeating the diagnosis.

### 5.4 Design Decisions

- **Changed:** ~~There is one~~ **One** format for ~~making~~ a structured request. The structure (Section 1.5.2) is the same for the classifier, the retrieval engine and the chatbot. This was by far the most helpful individual decision for integration.
- **Changed:** ~~Failure to any~~ **A fallback for every** external dependency. Language-model calls ~~go~~ **fall** back to ~~Grok,~~ **Groq,** and speech recognition ~~goes~~ **falls** back **through** three ~~layers.~~ **tiers.** When ~~the~~ **no** language model is ~~not~~ available for the advisory, the system ~~can answer based on~~ **answers from an offline guide and** the retrieved CCRI text alone. The fallbacks are ~~validated~~ **tested** and not taken for granted.
- **Changed:** **Caching by request.** A SHA-256 cache key **built from the image, the user, the language and the query** is used to serve the CNN result for ~~the same request, using the image, the user, the language and the query. Note that there~~ **a repeated request. The query** is ~~a query associated with~~ **part of** the key ~~since~~ **because** an early version without ~~this would result in~~ **it produced** collisions.
- **Changed:** ~~If~~ **Honesty when** the model ~~doesn't know, be honest.~~ **is unsure.** The system does not ~~consider~~ **treat** the label **as** settled if the top confidence is below ~~75 percent, so it goes to~~ **75%, and gives** broader ~~guidance. It~~ **guidance instead. The threshold** is ~~tunable~~ **tunable,** and the score ~~against~~ **with** which it is compared is not a calibrated probability, which is kept in mind ~~all the way. Never invent inputs:~~ **throughout. No invented inputs.** When no GPS is provided, the system does not generate ~~a~~ fake ~~weather~~ **weather,** and when ~~the~~ **a** number is not in the retrieved text, the system does not ~~call a~~ **mark the** dose as verified.

### 5.5 Client and Deployment

- **Changed:** The client is a single ~~Web Application~~ **web application** wrapped with Capacitor 7 for Android. It can ~~either be~~ **run as** a ~~progressive~~ web app in the ~~browser,~~ **browser** or **be** installed as an APK. In this ~~configuration~~ **configuration,** the app ~~is accessed by~~ **reaches the backend through** a ~~dynamic IP~~ **server** address ~~to the backend.~~ **that can be set at run time.** The one-tap phone, ~~maps~~ **Maps** and WhatsApp actions are ~~also~~ made possible by the Android wrapper, ~~as it can provide~~ **which passes** those links ~~as intents~~ to the ~~OS.~~ **operating system as intents.**

### 5.6.1 Module 1: Leaf Pathology

- **Changed:** Module 1 is based on a ~~ResNet model~~ **pre-trained ResNet-50** that is ~~pre-trained~~ **fine-tuned** to classify ~~5 different types of~~ **five** leaf ~~diseases and has~~ **conditions, with** a fixed ~~resolution of~~ input ~~images,~~ **resolution,** accuracy requirements and a confidence threshold. **Its design parameters are listed in Table 5.2.**

### 5.6.2 Module 2: Advisory Engine

- **Changed:** Module 2 recommends ~~disease~~ **treatments** based on semantic and keyword ~~based~~ retrieval, fuses **the** results **with reciprocal rank fusion, and adds weather context, language-model responses and dosage safety checks. Its design parameters are listed in Table 5.3.**
- **Removed paragraph:** ~~with reciprocal rank fusion and adds weather context, responses from language models and~~
- **Removed paragraph:** ~~dosage safety checks.~~

### 5.6.3 Module 3: Chatbot

- **Changed:** ~~The~~ Module 3 ~~comes with~~ **provides** a multilingual ~~chatbot,~~ **chatbot with an** 8-turn conversational ~~context, three speed~~ **context and a three-tier speech recognition fallback, and it supports Kannada, Kanglish and English. Its key figures are listed in Table 5.4.**
- **Removed paragraph:** ~~levels of speech detection, and supports Kannada, Kanglish and English.~~

### 5.6.4 Module 4: Marketplace

- **Changed:** With direct buyer–grower listings, photo galleries, proximity sorting, search filters and **contact information, Module 4 offers a farmer-friendly marketplace that makes trade easier. Its features are listed in Table 5.5.**
- **Removed paragraph:** ~~contact information, Module 4 offers a farmer-friendly marketplace for easier transactions.~~

### PROPOSED METHODOLOGY

- **Changed:** This chapter explains the ~~methods~~ **method** chosen for each ~~models~~ **module** and the reason ~~as well.~~ **for each choice.**

### 6.1.1 Why ResNet-50

- **Changed:** ResNet-50 was chosen because it is well understood, transfers well from ImageNet to leaf photographs, and fits on a laptop GPU for both training and serving. It is ~~characterized~~ **characterised** by the residual connection. ~~A bit of~~ **Each block learns a small** correction ~~is learned in each block, then~~ **and** the input is **then** added back, so that gradients are maintained in a deep network and training is much less fragile than **with** a plain stack of fifty layers. **The residual connection is given in Equation (6.1).**
- **Changed:** ~~Equation(6.1)~~ Here F(x) is what the block's layers compute and x is the input carried over the skip connection. If a block has nothing useful to add, it can learn F(x) close to zero and simply pass its input through.

### 6.1.2 Classification Head and Softmax

- **Heading:** `6.1.2 Classification head and softmax` → `6.1.2 Classification Head and Softmax`
- **Changed:** The network is a fine-tuned ResNet-50 whose original 1000-class head has been replaced by a dropout layer with probability 0.4 followed by a linear layer from 2048 features to 5 outputs. The Phase 2 prototype used a dropout of 0.3. It was raised to 0.4 as a modest step against the generalisation gap discussed in Chapter 8. Raw scores are turned into class probabilities with ~~softmax.~~ **the softmax function in Equation (6.2).**
- **Changed:** ~~Equation(6.2)~~ Here z is the vector of raw scores from the final layer and c is a class. The probabilities add up to one, which one of the tests checks explicitly.

### 6.1.3 Preprocessing

- **Changed:** Every image, whether from training or from a user, goes through the same sequence: convert to RGB, resize to 224 by 224 pixels, convert to a tensor and normalise with the ImageNet mean and standard ~~deviation.This is~~ **deviation. This matters** more ~~important~~ than it might ~~sound,~~ **seem,** because ~~it is~~ a model's ~~training~~ **serving** inputs ~~that~~ must match its ~~serving~~ **training** inputs. **Before this, every upload passes an image guard that checks the file signature and size limits, removes metadata such as GPS coordinates and re-encodes the image as a clean JPEG.** A test ~~is performed on the corrupted/unreadable~~ **covers corrupted and unreadable** uploads, ~~and if it fails, they~~ **which** are rejected cleanly ~~rather than causing a crash to~~ **instead of crashing** the request.

### 6.1.4 The SHA-256 Result Cache

- **Heading:** `6.1.4 The SHA-256 result cache` → `6.1.4 The SHA-256 Result Cache`
- **Changed:** Rerunning the network for the same request ~~will waste~~ **wastes** time and GPU ~~usage. The module thus calculates a~~ **capacity. A** SHA-256 hash of the image, the user, the language and the ~~query. The return~~ **query** is **therefore calculated by the module, and** the previous result **is returned** if this hash has been stored before. The query and language are ~~a~~ part of the key on purpose: a first version hashed less, and a test showed that two different questions about the same image could land on the same ~~entry~~ **entry.**

### 6.1.5 The Confidence Gate

- **Changed:** A classifier ~~will~~ always ~~output~~ **outputs** a most likely class, even ~~if~~ **for an input unlike anything** it has ~~never encountered anything exactly like the input. Top~~ **seen before. The top** softmax confidence **is therefore compared** with ~~the~~ **a** threshold of ~~75 percent is considered. It is followed by a~~ **75%. Below it, the** system ~~that~~ does not ~~agree~~ **commit** to a specific disease and provides more general advice. ~~There~~ **In the current build, a result is also marked uncertain when a disease is predicted but the best retrieved passage scores below 0.60, so that weak evidence is flagged as well. Two caveats** are ~~two warnings~~ on ~~the~~ record. ~~The first is that~~ **First,** 75% is a ~~tuneable~~ **tunable** value and **was** not ~~one that has been~~ taken from a calibration study. ~~Secondly, the Softmax~~ **Second, softmax** outputs are not true probabilities, so ~~it is~~ **a confidence of 75% does** not ~~exactly correct to say~~ **mean** that the model is correct ~~80 percent~~ **75%** of the ~~time~~ **time.**

### 6.2.1 Purpose

- **Changed:** After **a disease has been identified,** the grower ~~has identified a disease, he or she~~ must know what to do about it. The key principle of this module is that the answer should be drawn from "trusted text" and not from what the language model can recall. The model is used to write the advice in readable ~~form~~ **form,** but the facts it writes are retrieved first, following the retrieval-augmented generation pattern.

### 6.2.2 Live Microclimate and the Favourability Score

- **Heading:** `6.2.2 Live microclimate and the favourability score` → `6.2.2 Live Microclimate and the Favourability Score`
- **Changed:** Before retrieval starts, the module fetches **the** temperature, humidity and rainfall for the grower's coordinates from Open-Meteo. They are fed into a ~~basic rule of thumb~~ **simple rule-of-thumb** favourability score. The rule is based on the behaviour of ~~the~~ coffee leaf ~~rust disease,~~ **rust,** which ~~is spread~~ **spreads** when ~~coffee~~ **the** leaves are wet and the air is moderately warm (humidity ≥ ~~80 percent~~ **80%** and 20 to 28 ~~degrees Celsius). The learning~~ **°C). No learned** model ~~was not~~ **is** used here, ~~This~~ **so the rule** can be ~~communicated~~ **explained** to a grower and ~~can be evaluated~~ **checked** by an agronomist. It is also a coarse ~~instrument – not~~ **instrument,** based on the weather ~~at the estate but in~~ **of** the grid ~~– which~~ **cell rather than of the estate, and it** needs to be improved with on-farm sensors. The module ~~doesn't~~ **does not** guess: ~~If~~ **if there is** no GPS location, no weather goes into the prompt and no weather advisory is generated. **The current build reports the score as a high, moderate or low risk level (high when the rule above holds, moderate when the humidity is at least 65% or it has rained that day) and recommends a spray window from the three-day forecast.**

### 6.2.3 Three-Stage Hybrid Retrieval

- **Heading:** `6.2.3 Three-stage hybrid retrieval` → `6.2.3 Three-Stage Hybrid Retrieval`
- **Changed:** Retrieval runs in three ~~stages~~ **stages,** as shown in ~~the~~ Figure 6.1.
- **Changed:** Stage 1: Dense and Sparse Search. The question is expanded with the disease name and searched twice. Dense search uses FAISS over ~~BGE-base-en~~ **bge-m3** embeddings **(BGE-base-en on a CPU)** and finds passages that match in meaning. Sparse search uses BM25 and finds passages that match in wording. Each returns its top ~~15.~~ **20.**
- **Changed:** Stage 2: Reciprocal Rank Fusion. The two ranked lists are merged with reciprocal rank fusion. A passage earns a score from each list that depends only on its rank, and the scores are added, so a passage that ranks high in both lists rises to the top without anyone having to compare the incompatible raw scores of the two methods. ~~60~~ **The constant** is ~~the constant . (6.3)~~ **60, as shown in Equation (6.3).**
- **Changed:** Stage 3: Cross-Encoder Rerank. A **cross-encoder (bge-reranker-v2-m3 on a GPU,** MiniLM ~~cross-encoder~~ **on a CPU)** reads the question and each candidate passage at the same ~~time,~~ **time** and rates the degree of match. A sigmoid ~~is used to squeeze~~ **squeezes** the score **into the range 0** to ~~be between 0 and 1,~~ **1 (Equation (6.4)). Passages on the diagnosed disease receive a small preference of 0.1 for ordering, near-duplicate passages are removed,** and the best 3 passages are retained.
- **Changed:** ~~(6.4)~~ There is a practical reason for the additional step. The cross-encoder is more precise but slower, ~~Fusion~~ **while fusion** is faster but coarser, so the cheap stage cuts the pool from the entire index to a few ~~dozen,~~ **dozen passages and** the expensive stage cuts ~~the index~~ **it** down to the top three.

### 6.2.4 Generating the Answer

- **Heading:** `6.2.4 Generating The Answer` → `6.2.4 Generating the Answer`
- **Changed:** The prompt is made up of the disease, the weather summary, the three passages and the user's question, and Gemini 2.5 Flash writes the advisory. The free Gemini tier **supports** only ~~supports approximately~~ **about** 20 requests per day, so the module cannot ~~solely~~ rely on ~~this tier. Should~~ **it alone. If** Gemini ~~fail~~ **fails** or the quota ~~expire,~~ **runs out,** the call ~~will then go~~ **goes** to a 120B ~~model. It can run~~ **model (gpt-oss-120b) hosted** on ~~Grok,~~ **Groq;** if that is **also** not possible, **the** system ~~can display~~ **displays an offline guide for the disease together with** the retrieved CCRI ~~text directly.~~ **text.** During ~~the test,~~ **testing,** the quota did ~~expire,~~ **run out,** but the fallbacks ~~were such~~ **ensured** that all tests passed.

### 6.2.5 The Dosage Audit

- **Changed:** The most critical mistake in ~~an~~ agricultural advice is a ~~misdose.~~ **wrong dose.** To ~~minimize it,~~ **minimise this risk, every dosage in the final answer is extracted by** a regular-expression check ~~is performed on the final answer to find dosages, while searching~~ **and searched** for ~~each dosage~~ in the retrieved CCRI passages. The advisory is marked ~~as~~ "Verified" if ~~all the dosages are~~ **every dosage appears** exactly ~~the same~~ as in the ~~source.It means that the advisory is marked "Verified"~~ **source;** if ~~all the dosages are exactly the same as in the source.If~~ any dosage cannot be found, it is labelled ~~Caution. The audit has a limited scope, and it is important not to overstate it. It confirms that a quantity is present in the source text, which catches invented numbers. It does not check whether the quantity is agronomically right for the grower's situation, whether the source is current, or whether the number belongs to the right product.~~ **"Caution".**
- **Changed:** ~~In Phase 2, answer quality was measured by asking~~ **The audit has** a ~~domain expert~~ **limited scope, and it is important not** to ~~score the answers to 30 query-reference pairs; answers given~~ **overstate it. It confirms that a quantity is present** in the ~~hallucination condition produced a 6.7 percent hallucination rate, while answers without retrieval had a 43.3 percent rate of hallucination. The same expert evaluation of~~ **source text, which catches invented numbers. It does not check whether** the ~~Phase 3 pipeline was not conducted. The automatic dosage check and~~ **quantity is agronomically right for** the ~~automated tests (which check behaviour but are not a substitute for another round of expert review) are added~~ **grower's situation, whether the source is current, or whether the number belongs** to ~~Phase 3.~~ **the right product.**
- **Added paragraph:** In Phase 2, answer quality was measured by asking a domain expert to score the answers to 30 query-reference pairs; answers generated with retrieval had a 6.7% hallucination rate, while answers without retrieval had a 43.3% hallucination rate. The same expert evaluation was not repeated for the Phase 3 pipeline. Instead, Phase 3 adds the automatic dosage check and the automated tests, which check behaviour but are not a substitute for another round of expert review, together with the automated benchmark reported in Section 8.6.

### 6.3.1 Role of the Chatbot

- **Heading:** `6.3.1 Role of the chatbot` → `6.3.1 Role of the Chatbot`
- **Changed:** The advisory engine ~~provides~~ **gives** one answer to one scan, but a grower wants to have a ~~conversation, what~~ **conversation: "What** if ~~tomorrow~~ it rains ~~– "Can I Spray Now, How Much Does It Cost Me For The Small Plot".~~ **tomorrow?", "Is it safe to spray now?", "How much is needed for a small plot?".** The chatbot ~~does just that.~~ **handles exactly this.** It ~~will listen for~~ **accepts** voice or text in Kannada, Kanglish or English, ~~remember what~~ **remembers** the ~~previous person had said~~ **earlier turns of the conversation** and **has** access **to** the scan and weather that ~~initiated the conversation.~~ **started it.**

### 6.3.2 The Linguistic Pre-Router

- **Heading:** `6.3.2 The linguistic pre-router` → `6.3.2 The Linguistic Pre-Router`
- **Changed:** ~~Our~~ **The** Phase 2 plan was to produce advice in English and have ~~this~~ **it** translated by a second model call, **which added** a second source of ~~error,~~ **error and** a delay. In Phase 3, a ~~tiny part is used to deal with language, which is known as~~ **small component called** the ~~pre-router.~~ **pre-router handles language.** It validates the query and checks ~~to see if~~ **whether** it contains Kannada script using Unicode character ranges. This regular-expression check takes under a millisecond (0.08 ms ~~in our measurement)~~ **as measured)** to run. **In the current build, the router first asks the language model, in a short JSON-mode call, for the language and one self-contained English search question, and it also receives the last two exchanges so that follow-up questions are understood; the Unicode check is used when the language model is unavailable.**
- **Changed:** For a Kannada query the pre-router does two things. It creates an English query for the retrieval engine ~~(as~~ **(because** the knowledge base is written in English), and it appends an instruction for the language model to ~~return an~~ answer in Kannada ~~characters. There~~ **script. No separate translation of the answer** is ~~no need for a translation call in retrieval~~ **needed,** because only the ~~last step~~ **final reply** is in ~~a different language. Its disadvantage~~ **Kannada. The drawback** is that ~~it uses~~ the **system relies on the written** Kannada ~~writing~~ of the language model, which is good but not ~~perfect Native speaker~~ **perfect;** validation **by native speakers** should be ~~considered in any~~ **part of** future work.

### 6.3.3 Voice Input with a Three-Tier Fallback

- **Heading:** `6.3.3 Voice input with a three-tier fallback` → `6.3.3 Voice Input with a Three-Tier Fallback`
- **Changed:** The chatbot ~~features~~ **accepts voice input and uses** three ~~fallback mechanisms for reliable~~ **tiers of** speech ~~recognition in case~~ **recognition, so that a failure of** the main method ~~fails, and can accept voice input.~~ **does not leave the grower without a transcript.** The ~~least successful~~ **weakest** aspect of Phase 2 was the speech recognition ~~system~~ **system,** which achieved less than ~~55 percent~~ **55%** accuracy ~~in~~ **on** Kannada words in the disease vocabulary. In Phase 3 the single **browser** recogniser ~~of the browser~~ was replaced by a ~~three-tiered browser recogniser~~ **three-tier chain** (Figure 6.2 and Table 6.1). ~~First resamples the~~ **The** audio **is first resampled** to 16 ~~kHz,~~ **kHz** and then ~~attempts~~ **passed** to ~~play it against~~ each tier in order until **one succeeds. The transcript is placed in the input box for the grower to correct;** it ~~passes.~~ **is never sent automatically.**
- **Changed:** Putting the local model first has two ~~benefits.It~~ **benefits. It** does not ~~require high quality~~ **depend on a good** network ~~connections~~ **connection** or **on** API ~~quotas~~ **quotas,** and for ~~Kannada. It has~~ **Kannada it uses** a model developed for Indian languages. **The published word error rate of the** Kannada model ~~published WER~~ is ~~12.4 per cent. Our current work does~~ **12.4%; it has** not ~~report or measure farmer recordings.~~ **been measured on farmers' recordings in this work.** The cloud tiers ~~are there in case of~~ **cover a** failure of the local model, so that the grower is not left with nothing.

### 6.3.4 Context Fusion

- **Heading:** `6.3.4 Context fusion` → `6.3.4 Context Fusion`
- **Changed:** The chatbot ~~will~~ **does** not reply to a message ~~alone.~~ **in isolation.** For each request, one prompt is composed from ~~4~~ **four** sources: the previous 8 turns of the conversation, the current weather ~~for~~ **at** the grower's location, the current CNN ~~diagnosis,~~ **diagnosis** and the ~~last~~ passages retrieved by the hybrid RAG engine. The language rule is written in the last line. ~~Context is important for~~ **This context means that** the ~~diagnosis so that it is~~ **grower does** not ~~necessary~~ **need** to mention the disease when ~~a grower asks "how~~ **asking "How** bad is this?". The ~~8 turn~~ **8-turn** window is a compromise between the size of the ~~trade~~ **context** window and memory. The Phase 2 requirement was ~~that the added turns be~~ at least ~~10,~~ **10 turns,** so the shipped ~~count~~ **window** is slightly ~~less~~ **smaller** than ~~the original requirement.~~ **originally required.**

### 6.3.5 Visual Memory

- **Heading:** `6.3.5 Visual memory` → `6.3.5 Visual Memory`
- **Changed:** If the grower scans a ~~leaf~~ **leaf, moves to the chat** and then ~~goes to~~ **refreshes** the ~~chat, followed by a page refresh~~ **page,** the photo should ~~remain unchanged.~~ **still be there.** The chatbot ~~uploads~~ **saves** the leaf images ~~created~~ **sent** by the user **and links them to the user's thread, so that each thread keeps its images. In the current build the images are stored as sanitised files rather than** as Base64 strings ~~to~~ **inside the database, which keeps** the database **rows small** and ~~ensures that each user thread retains its images. This is not a scalable way to store large numbers of images, but it is simple, avoids a separate file store and works at~~ **removes any location metadata from** the ~~current scale.~~ **photos.**

### 6.4.1 What the Marketplace Does

- **Heading:** `6.4.1 What the marketplace does` → `6.4.1 What the Marketplace Does`
- **Changed:** The marketplace is where ~~a~~ **the** grower's ~~work~~ **harvest** is sold. A **grower lists a** lot of ~~coffee is listed by a grower and~~ **coffee,** a buyer finds ~~it. They~~ **it, and the two** contact each other directly. The module is deliberately ~~small. It can't~~ **small: it does not** process payments, ~~doesn't~~ **does not** charge any ~~commissions,~~ **commission** and ~~can't suggest any intermediaries~~ **places no intermediary** between ~~both~~ **the two** parties ~~when it comes to~~ **during** discovery. ~~It~~ **Its purpose** is to ~~get~~ **make** the first step ~~easy –~~ **easy:** to be visible, to be found by someone nearby and to start a conversation.

### 6.4.2 Listings

- **Changed:** A listing contains the variety of coffee, ~~amount of coffee,~~ **the quantity, the** price per ~~kilo,~~ **kilogram** and **the grower's** contact ~~info for~~ **details. Each listing can have a gallery of up to eight photos, each with a caption. Because growers trade in different units,** the ~~grower. There~~ **server converts quantities to kilograms and prices to rupees per kilogram, so that lots sold in bags, quintals or tonnes** can be ~~a multi-photo gallery with a caption for each photo for every listing. The photos and their captions are retained in a JSON format, allowing for a variable number of photos with a simple schema.~~ **compared.** Data is validated ~~prior to~~ **before** saving: ~~Price~~ **price** and quantity ~~can't~~ **must** be ~~below~~ **above** zero, and **the** phone number must be valid. ~~It~~ **This** may seem ~~like a no-brainer~~ **obvious,** but ~~this~~ **it** is where poor data ~~might~~ **would** otherwise ~~infiltrate~~ **reach** the ~~buyer's eyes.~~ **buyers.**

### 6.4.3 Finding Nearby Lots

- **Heading:** `6.4.3 Finding nearby lots` → `6.4.3 Finding Nearby Lots`
- **Changed:** In Phase 2 the design called for a PostGIS spatial index and a Node.js service. ~~During~~ **In** the final build, proximity is computed within the application using the Haversine ~~formula~~ **formula,** which ~~is used to calculate~~ **gives** the straight-line distance between two points on a ~~sphere.~~ **sphere (Equation (6.5)).**
- **Changed:** ~~Equation 6.5 In these,~~ **Here** φ is the latitude, λ is the longitude and R is the radius of the Earth (6371 km). For example, two town centres **in the coffee belt that are about 0.9 degrees of latitude apart** are separated by about 99 ~~km, and they are separated by about 0.9 degrees of latitude and belong to the coffee belt.~~ **km.** This is a ~~straight line~~ **straight-line distance,** and the road ~~length~~ **distance** will be greater. For each listing the app computes the distance from the buyer and sorts the results in ascending order. This is ~~quick~~ **fast** enough ~~at~~ **for** a regional marketplace ~~level,~~ and ~~doesn't~~ **does not** require a spatial database extension. If the number of listings ~~reach~~ **reaches** thousands, ~~then another~~ **a** spatial index would be worthwhile.

### 6.4.4 Filters and One-Tap Actions

- **Heading:** `6.4.4 Filters and one-tap actions` → `6.4.4 Filters and One-Tap Actions`
- **Changed:** The results can be filtered by a ~~dual-handle~~ price ~~slider, as well as by~~ **range, variety, minimum lot size, maximum distance and** a keyword search, each ~~of which is performed~~ **applied** as a database query. ~~They use~~ **These filters are combined with** distance ~~sorting to allow~~ **sorting, so** a buyer ~~to request a list of items, such as~~ **can ask for, say,** Arabica below a ~~specific price level and~~ **certain price,** nearest first. When a buyer has ~~discovered~~ **found** a lot, ~~there are~~ three actions ~~that~~ are ~~only a~~ **one** tap away: a Google Maps URL opens directions to the farm gate, a tel: link opens the phone dialler with the grower's number, and a wa.me link opens WhatsApp with a **pre-written** message ~~already written and~~ **containing** the lot ~~details encoded into it. That's where these~~ **details. These** hand-offs ~~come into play--after all, that's why~~ **are the reason** the web app was wrapped with ~~Capacitor. On~~ **Capacitor: on** Android the wrapper passes the links to the operating system, which opens the right app. For ~~this~~ **the same** reason, ~~it was decided not to build~~ in-app messaging ~~as it is something that~~ **was not built, because** growers and buyers ~~are~~ already ~~doing on a daily basis, and so is the case with~~ **use** WhatsApp and the phone ~~dialler.~~ **dialler every day.**

### 6.5.1 Use of Automated Testing

- **Changed:** In Phase 2 each module was tested by hand and ~~reported~~ the results **were reported** in tables. This was ~~just~~ enough to ~~demonstrate~~ **show** that the ideas ~~were effective,~~ **worked,** but ~~they~~ **it** would ~~never~~ **not** have ~~been able to be integrated. As soon as~~ **supported integration. Once** the modules started calling ~~to~~ one another, an error in one module could ~~be sufficient to~~ cause problems three steps away, and manual checking ~~was~~ **would** not ~~going to~~ catch ~~these errors.A heightened sense of~~ **such errors. The** responsibility was ~~felt, given that~~ **also greater because** the application ~~provides~~ **gives** chemical spraying recommendations and stores user account information, where inaccurate advice or **a** data ~~breaches~~ **breach** could have serious real-world ~~consequences..~~ **consequences.** In Phase ~~3~~ **3, therefore,** an automated suite was created ~~using~~ **with** pytest **for the backend, later joined by Vitest** and **Playwright for the frontend, and it** was ~~considered~~ **treated** as part of the product.

### 6.5.2 Schedule

- **Changed:** ~~The testing~~ **Testing** was ~~done for~~ **carried out** over eight weeks in four ~~sprints which first started~~ **sprints, moving** from ~~the~~ small units to the whole application (Table 6.2).

### 6.5.3 Test Methods and the Reason for Each

- **Heading:** `6.5.3 Test Methods Used and the Reasons` → `6.5.3 Test Methods and the Reason for Each`
- **Changed:** Table 6.3 ~~shows~~ **lists the test methods used: unit, functional, integration, security, performance, real-model, frontend and end-to-end tests. Together, 373 tests check that individual modules function properly, that** the system ~~tested using the Unit & functional testing, Integration testing,~~ **components are integrated correctly, that security is maintained and that performance is reliable.**
- **Changed:** ~~Security testing~~ **The integration tests exercise routing, authentication** and ~~Performance Testing. 48~~ **the database without starting a server, using the real application in memory with the FastAPI test client. The performance** tests ~~were done to ensure that individual~~ **are marked hardware-dependent, because their figures reflect the laptop used rather than a universal property of the code.**
- **Removed paragraph:** ~~modules function properly, to ensure that the system components are integrated properly, to~~
- **Removed paragraph:** ~~ensure security is maintained, and to ensure performance is reliable.~~
- **Removed paragraph:** ~~The integration tests exercise routing, authentication and the database, without a server being started, using the real application in memory with test client from FastAPI. The performance tests are marked hardware-dependent since they are just the number of personal laptop used and not some universal feature of the code.~~

### IMPLEMENTATION AND PSEUDOCODE

- **Changed:** This **chapter** lists the technologies ~~used in the current work, and~~ **used,** describes how each module was ~~put together as~~ **implemented and integrated into** one ~~,~~ **system,** and gives the pseudocode ~~as well.~~ **for each module.**

### 7.1 Technology Stack

- **Changed:** ~~All tools are open source.~~ The ~~two hosting language models, Gemini and Groq, represent the key exception on the run time side, and what's partially met through the open source objective.~~ **technology used in each module is listed in Table 7.1.**
- **Added paragraph:** All tools are open source. The two hosted language models, Gemini and Groq, are the main run-time exception, which is why the open-source objective is only partly met.

### 7.2 Development and Test Environment

- **Changed:** ~~The entire development~~ **Development** and testing ~~was~~ **were** done **entirely** on a Windows 11 laptop equipped with ~~a~~ **an** NVIDIA RTX **3070 Laptop** GPU (CUDA 12) and Python 3.11. ~~The~~ **Language-model calls went first to Gemini and then to Groq, so the** fallback chain was ~~a test chain; It was~~ **exercised during normal testing and** not ~~possible to test it without invoking it when calls to Gemini were made first and Groq were made second.~~ **only in theory.**

### 7.3 Module 1: Leaf Pathology

- **Changed:** ~~Classifier:~~ **The classifier is a** PyTorch ~~ResNet-50, has been~~ **ResNet-50** modified with a **dropout layer (0.4) and a** linear layer ~~(from~~ **from** 2048 features to 5 ~~outputs) and dropout (0.4).~~ **outputs.** The saved model is approximately 94 MB. The uploaded image is converted to RGB, resized to 224 x 224, normalised and fed into the network. ~~Result~~ **The result** (class, confidence and ~~whole~~ **full** probability vector) is cached under the SHA-256 key in the cache table. Training and inference use the same preprocessing function to eliminate one common source of silent error. **The procedure is given in Algorithm 7.1.**

### 7.4 Module 2: Advisory Engine

- **Changed:** The retrieval code ~~creates~~ **builds** two ~~different~~ indexes ~~for~~ **over** the same CCRI passages, one from ~~BGE-base-en~~ **bge-m3** vectors and another from the tokenised text using BM25. The microclimate service fetches ~~data from Open-Meteo and provides~~ **the** temperature, humidity and rainfall **from Open-Meteo,** which ~~is~~ **are** used to calculate the favourability rule. ~~First the~~ **The** generator ~~attempts~~ **first tries** Gemini 2.5 ~~Flash to generate the text, then~~ **Flash;** if it fails or reaches its ~~text generation~~ limit, it ~~will fall~~ **falls** back to the Groq-hosted model, and finally to the **offline guide and the** retrieved text. ~~A no-response~~ **An empty response** from a model is ~~considered~~ **treated as** a failure and leads to the next ~~failure. The dosage audit extracts quantities of the answer using a regular expression and ensures that each quantity appears in the answer retrieved. In the first version of the pattern, the word-boundary marker (which does not match immediately following percent sign) meant that percentage doses were not included. The boundary logic was rewritten and a regression test was added.~~ **fallback.**
- **Added paragraph:** The dosage audit extracts quantities from the answer using a regular expression and checks that each quantity appears in the retrieved passages. In the first version of the pattern, the word-boundary marker (which does not match immediately after a percent sign) meant that percentage doses were missed. The boundary logic was rewritten and a regression test was added. Number words are now also converted to digits, so that "four litres" is audited as "4 L". The complete procedure is given in Algorithm 7.2.

### 7.5 Module 3: Chatbot

- **Changed:** The ~~pre-router is~~ **language router asks the language model for the language of the message and one English search question, and falls back to** a short ~~Regular-Expression~~ **regular-expression** function over Unicode character ranges. ~~If~~ **For** a ~~query was made in Kannada, it translates~~ **Kannada query,** the ~~query into~~ English **question is used for retrieval** and ~~then adds the~~ **an** instruction to ~~return the results~~ **answer** in Kannada ~~script.~~ **script is added.** Audio is resampled to 16 kHz and handed to the speech chain. The conversation history, ~~weather,~~ **weather and** latest diagnosis are merged ~~and~~ **with** the retrieved passages ~~are added to this~~ **into the** prompt. ~~This includes Base64 leaf~~ **Leaf** images ~~that~~ **sent in the chat** are saved ~~using~~ **as sanitised files and linked to the thread through** SQLAlchemy. **One chatbot turn is given in Algorithm 7.3.**

### 7.6 Module 4: Marketplace

- **Changed:** The marketplace is a FastAPI router over SQLAlchemy models. ~~Photo galleries~~ **Photos** are stored as ~~a JSON list of objects~~ **sanitised files,** with ~~a URL and a caption.~~ **their captions in the database.** Distance is computed in Python for each listing, and the Maps, tel: and wa.me links are generated on the server and opened through Android intents by the Capacitor wrapper. **Listing creation and the nearby search are given in Algorithm 7.4.**

### 7.7 Test Suite Implementation

- **Changed:** Each team member was responsible for developing and maintaining **the** tests for their ~~respective modules(Table~~ **own module (Table** 7.2), and the cross-cutting tests were written jointly. The integration tests use ~~FastAPI's~~ **the FastAPI** test client, the data layer runs on SQLAlchemy, ~~and~~ Pillow generates the synthetic and corrupted ~~images.~~ **images, and Vitest and Playwright test the frontend.**
- **Changed:** The testing tools used and the ~~roles they play~~ **role each plays** in validating the system are ~~summarized~~ **summarised** in **Table 7.3.**
- **Changed:** ~~table 7.3.~~ These tools ~~aid in testing~~ **help to test** the functionality of the APIs, model performance, **retrieval accuracy, database security and image processing, ensuring that the system works reliably across all modules.**
- **Removed paragraph:** ~~retrieval accuracy, database security, and image processing, ensuring the system's reliability~~
- **Removed paragraph:** ~~and smooth functioning across all modules.~~

### 7.8 Benefits and Drawbacks of the Approach

- **Changed:** Benefits. The ~~entire~~ **fast backend** suite ~~takes about 103 seconds to finish,~~ **runs without a GPU, using deterministic fakes for the models,** so it was possible to run it after nearly every change. ~~It~~ **Real bugs were** discovered ~~real bugs,~~ **by the suite,** such as cache-key ~~collisions (Section 8.4),~~ **collisions,** the failure to audit ~~for~~ percentages ~~(Section 8.5)~~ and the absence of a guard ~~to prevent~~ **against** an empty language-model reply (Section ~~8.6). It also confirmed the~~ **8.4). The** zero-mock weather rule and ~~returning a~~ **the** 403 response ~~if~~ **returned when** a user attempts to access another user's data **were also confirmed,** for the cases tested.
- **Changed:** Drawbacks. Some ~~GPUs~~ tests require NVIDIA ~~hardware but there is~~ **hardware, although** a ~~fall-back in case of CPU.~~ **CPU fallback exists.** The free tier of Gemini ~~has~~ **is** limited ~~requests~~ to about 20 requests per day, so fallbacks to Groq and local resources were needed. The **fast** tests rely on ~~artificial~~ **synthetic** leaf ~~images, not~~ **images rather than** a large ~~group~~ **set** of actual field photographs, ~~and~~ so they ~~don't~~ **do not** report ~~what~~ the accuracy of the diagnosis ~~is~~ in the ~~field..~~ **field.**

### 8.1 Expected Versus Actual Results

- **Changed:** Targets ~~are Set~~ **were set** before ~~running~~ the final test ~~pass~~ **run** and compared ~~them~~ with ~~what was measured.~~ **the measured values, as shown in Table 8.1.**
- **Changed:** ~~There are two~~ **Two** points ~~to note~~ **should be noted** about this table. First, the results "0 leaks" and "401 on tested routes" refer to the cases ~~that~~ **for which** tests were ~~written for.~~ **written.** They **confirm that the tested paths are secure, but they** do not ~~demonstrate~~ **guarantee** that ~~these~~ **untested paths** are ~~the only paths that are safe, but rather that these are safe paths. Secondly,~~ **free of vulnerabilities. Second,** the performance figures ~~are~~ **come** from a single laptop and can ~~vary~~ **differ** elsewhere.

### 8.2 Accuracy of the Classifier

- **Changed:** The CNN achieved a validation accuracy of ~~90 percent,~~ **90%** and ~~a test~~ **an** accuracy of ~~80 percent~~ **80%** on new leaf ~~images (Figure 8.1). The accuracy~~ **images. A later leak-free five-fold cross-validation** on the ~~validation set~~ **public JMuBEN images measured an accuracy of 97.9%** and ~~new leaf images is~~ **a macro-F1 of 0.970. These results are** compared in ~~figure 8.1, it is about~~ **Figure 8.1.**
- **Changed:** ~~90% and 80% respectively.~~ The results show that the model ~~is able to give~~ **reaches** a good accuracy on the **validation** data ~~used for validation~~ and ~~a good generalization for the~~ **generalises reasonably to** unseen ~~data of the~~ leaf images. The validation score ~~tells us~~ **shows that** the model learned its training ~~distribution.The~~ **distribution. The** new-leaf score is closer to what a grower will see, and the 10-point difference is likely due to ~~varying~~ features ~~(background~~ **such as background** or ~~lighting)~~ **lighting** that ~~are~~ **do** not always ~~transferable~~ **transfer** to a new photo. A **model** trained ~~model that is optimized for~~ **on** a ~~combination~~ **mix** of clean and field images ~~will perform~~ **performs** best on **data** similar ~~data such as the~~ **to its** training set, ~~and a real~~ **while an actual coffee** estate ~~will include~~ **includes variable** lighting, soil splashes, partial leaves and overlapping foliage that ~~are not captured by any~~ **no** curated ~~set.~~ **set captures.** The same pattern was observed in Phase ~~2 and the paper in the field image is warned by the Grenze CNN [3].~~ **2.**
- **Changed:** ~~Per-class precision/recall for~~ **The leak-free evaluation was added because an audit of** the ~~final model has not been calculated~~ **JMuBEN dataset found that its 58,549 files come from only 861 distinct leaf patches, so a random split places a copy of almost every test image** in ~~this report~~ **the training set. With every copy of a patch kept on the same side of each fold, the classifier reaches an accuracy of 97.9%. The hardest pair is Phoma Blight** and ~~it cannot be claimed that one disease can be recognised more effectively than another. The practical solution the system gives to the gap, is the 75 percent confidence gate: when the model does not know the advice becomes wider~~ **leaf miner,** and the ~~model does not claim to be specific. So~~ **F1-score for Phoma Blight is 0.949. At** the ~~prudent thing to do is to gather more field photos, leave~~ **75% confidence gate,** the ~~gate up and show~~ **classifier answers 99.3% of** the ~~results as a decision aid to be verified~~ **images,** with an ~~agronomist.~~ **accuracy of 98.1% on those it answers. These images are close-up, evenly lit patches from a single dataset, so the figure is an upper bound for field photographs.**
- **Added paragraph:** Per-class precision and recall on field photographs have not yet been calculated, so it cannot be claimed that one disease is recognised in the field more reliably than another. The practical answer that the system gives to the gap is the 75% confidence gate: when the model is unsure, the advice becomes broader and the model does not claim to be specific. The prudent course is therefore to gather more field photos, keep the gate in place and present the results as a decision aid to be verified with an agronomist.

### 8.3 Speed

- **Changed:** ~~Table 8.2 shows the~~ **The** measured response times ~~for various system~~ **of the main** operations ~~such as script~~ **are listed in Table 8.2 and plotted in Figure 8.2.**
- **Changed:** ~~detection, CNN cache hit, warm inference and cold starts.~~ The ~~outcomes~~ **results** show that **cached requests and lightweight checks are processed almost instantly, while** the **CNN cold start takes longer because of the initialisation of the GPU.**
- **Changed:** ~~system~~ **A cache hit** is ~~quick~~ **about six times faster than a warm inference on the GPU (0.85 ms compared with 5.3 ms)** and ~~efficient,~~ **over 800 times faster than a cold start. All of these numbers are small compared** with ~~cached~~ **the language-model call and the network, which dominate the time that the grower waits for a complete advisory (about 6 s). The speed-ups matter mainly when many users repeat** requests and ~~lightweight checks being processed in a timely manner and CNN cold starts taking longer due to~~ **load** the ~~initialization of the GPUs.~~ **GPU.**
- **Removed paragraph:** ~~A cache hit is 17 times faster than a warm inference (0.85 ms compared with 14.2 ms) and over 800 times quicker than a cold start. All of these numbers are small in absolute terms, compared to the language-model call and the network which dominate the numbers that the grower is waiting for. The speed-ups only really have importance when there are many users repeating requests for the GPU load.~~
- **Removed paragraph:** ~~Table 8.3 identifies the major design features of the system and their benefits as compared to traditional systems, which boost safety, accuracy, efficiency and access for farmers. The most similar system is the one used in RAG-based coffee remediation. PlantIQ follows the same concept of getting the disease label matched with retrieval with Kannada voice and script handling, live weather input and a direct marketplace and a dosage audit. It should be mentioned that this comparison is not "equal opportunity" per se. It provides a comparison of the design options and properties that were measured, including the latency and the behaviour of the audit. It's not a comparison of the two systems on the same set of data and it cannot be claimed to be more accurate than anybody else.~~

### New section: 8.4 Deviations and What Was Learned

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> Several results differed from the plan, and most of these deviations were found by the automated tests or the benchmarks. Each is described below together with the action taken.

### New section: 8.4.1 CNN Cold Start

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> The first CNN call after start-up took 704 ms against a target of 100 ms, because it includes the initialisation of CUDA. Later calls take a median of 5.3 ms on the GPU. The target was missed, and a warm-up call at start-up is planned (Section 9.8).

### New section: 8.4.2 Cache-Key Collisions

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> An early version of the result cache built its key from too few inputs. A test showed that two different questions about the same image returned the same cached answer. The language and the query were added to the key, and the test now guards against the regression.

### New section: 8.4.3 Percentages Missed by the Dosage Audit

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> The first audit pattern used a word-boundary marker that does not match immediately after a percent sign, so percentage doses such as 1% were never checked. The boundary logic was rewritten and a regression test was added. A later benchmark showed that doses written in words, such as "four litres", were also missed; number words are now converted to digits before the check.

### New section: 8.4.4 Empty Language-Model Replies

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> Gemini 2.5 Flash sometimes spent its output budget on internal "thinking" tokens and returned an advisory cut short at about 100 characters. Thinking was turned off and the output budget was raised. An empty reply, or a reply that stops at the token limit, is now treated as a failure that moves the request to Groq.

### New section: 8.4.5 Language-Model Quota

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> The free Gemini tier allows about 20 requests per day, and the quota ran out during testing. The Groq fallback and the offline guide kept every test passing, which confirmed that the fallback chain works in practice and not only on paper.

### New section: 8.4.6 Chatbot Faults Found by the Benchmark

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> Three faults were exposed by the chatbot benchmark. The language router saw only the current message, so two of ten follow-up questions were answered wrongly; weather keywords matched inside two Kannada compound words; and the offline reply for Kannada users quoted English excerpts. The router now receives the last two exchanges, weather keywords must start a word, and the offline Kannada reply cites the document pages in Kannada. Regression tests were added for all three fixes.

### New section: 8.5 Field Feedback

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> An initial round of field testing was carried out with coffee planters who were willing to try the application and give their honest feedback. Their comments on usability were positive. The round was informal: no task-completion or time-on-task figures were recorded, and the number of participants was small. A structured pilot with more growers and buyers is planned (Section 9.8).

### New section: 8.6 Comparison with Common Alternatives

No heading with this number was matched in the original (new section, or a heading whose number or title changed). Full text in the fixed copy:

> Table 8.3 compares the major design choices of the system with typical alternatives; together, these choices improve safety, accuracy, efficiency and access for farmers.
> The closest design is a pipeline that matches a disease label with dense retrieval. PlantIQ follows the same idea and adds Kannada voice and script handling, live weather input, a direct marketplace and a dosage audit. Table 8.3 is not a like-for-like contest: it compares design options and the properties that were measured, such as latency and the behaviour of the audit.
> To compare the retrieval designs on equal terms, a dense-only pipeline was re-implemented and run on the same questions with the same language model; the results are given in Table 8.4. On 75 Karnataka coffee questions (21 of them in Kannada), the hybrid retriever found the gold evidence in its top three passages for 0.867 of the questions, against 0.500 for dense-only retrieval. With the same language model, the PlantIQ answers were correct for 0.944 of 54 English questions, against 0.824 for the dense pipeline and 0.611 without retrieval; without retrieval, 20.4% of the answers stated a dose that was not in any supplied document, against none for PlantIQ. On 43 test conversations, the chatbot behaved as expected in all 43, against 15 for a conversational chain built on the dense pipeline.
> The answers and their scores were produced by a single language model from the exact prompts of each system, and the questions were written from the same documents, so these figures should be confirmed with human judges and a question set collected from growers.

### 8.7 Limitations

- **Changed:** The following limitations have been identified and ~~consistently~~ **are** acknowledged throughout the report.
- **Changed:** ~~Fictional~~ **Synthetic** test data: The ~~automatic~~ **fast automated** tests ~~are based on purposefully distorted~~ **use synthetic** and ~~synthetic~~ **deliberately corrupted images; only the four real-model tests use real sample photographs.**
- **Changed:** ~~1. images.~~ **Classifier generalisation: A gap between 90% on validation and 80% on new leaves was observed, indicating that field performance is lower than laboratory performance, and the leak-free 97.9% was measured on close-up patches from one dataset. The softmax confidence is not calibrated, and the 75% gate is a tunable value rather than a statistically derived one.**
- **Changed:** ~~2. Classifier generalization: A difference between 90 percent on validation~~ **Dosage audit scope: The audit verifies that a quantity appears in the retrieved text. It does not check whether the amount suits the context,** and ~~80 percent on new leaves is observed indicating that field performance is less than laboratory performance. The softmax level of confidence is not calibrated and~~ **it cannot prevent a mistake in** the ~~75 percent gate is a tunable value and not a statistical value.~~ **source text.**
- **Changed:** ~~3. Dosage audit scope:~~ **No separate grading of Kannada quality:** The ~~audit verifies~~ **12.4% word error rate is** a ~~quantity in~~ **published figure for** the ~~retrieved text. It does~~ **model. The Kannada text generated by the language model has** not ~~check if the amount~~ **yet been formally reviewed by native speakers, and there** is ~~adequate to the context and it will not prevent a mistake in the source text.~~ **no measure of speech accuracy on farmers' recordings.**
- **Changed:** ~~4. No separate grading for Kannada quality: The 12.4 percent word error rate is a published figure~~ **External service dependence: Hosted language models are used** for the ~~model.~~ **advisory.** The ~~Kannada text generated by~~ **free Gemini tier allows only about 20 requests per day, so** the ~~language model has not yet been formally reviewed~~ **Groq** and ~~judged by native speakers of~~ **offline fallbacks are crucial, and service changes or pricing may affect** the ~~language and we don't have any measure of speech accuracy on farmers' recordings.~~ **system.**
- **Changed:** ~~5. External service dependence: Hosted language models are used for~~ **Grid-level weather: Open-Meteo provides weather at grid level. The rule is therefore coarse, because it does not reflect** the ~~advisory. The free tier, Gemini, provides for just approximately 20 requests per day, so the Groq fallbacks and the CCRI fallbacks are crucial and service changes~~ **microclimate of a specific slope, shade level** or ~~ticket pricing may impact the system.~~ **stream.**
- **Changed:** ~~6. Grid-level weather: Weather~~ **Restricted range of conditions and inputs: The classifier covers five leaf conditions. Soil** data is ~~available at grid level with Open-Meteo. It~~ **not used in the current build, and severity** is ~~a coarse rule since it does~~ not ~~reflect a microclimate of a specific slope, shade level or stream.~~ **assessed.**
- **Changed:** ~~7. Restricted range of conditions and inputs: The classifier consists of five leaf condition. In the current build, soil data and elevation are not utilized, and severity is not assessed.~~ Small field trial: ~~The~~ **Only an** initial round ~~is~~ with ~~the~~ coffee planters **has been carried out,** and ~~field feedback is received.~~ **structured usability metrics have not yet been collected.**
- **Changed:** ~~8. Structured usability metrics have~~ **No transactions: The marketplace connects growers and buyers but does** not ~~yet been established.~~ **handle contract negotiation or payment.**
- **Changed:** ~~No transactions: The marketplace~~ **Server dependence: Diagnosis requires access to the backend, so growers in valleys without adequate coverage cannot use it until offline support** is ~~meant to connect growers and buyers but it is not~~ **added.**
- **Changed:** ~~9. involved in contract negotiations or accepting payment.~~ **Hardware-dependent performance: Latency figures were measured on one laptop with an NVIDIA GPU and are therefore indicative.**
- **Changed:** ~~10. Server dependence: Diagnosis requires backend access,~~ **Benchmarks written by the team: The retrieval and chatbot questions were written from the knowledge-base documents and scored by a language model,** so **a question set collected from** growers ~~in valleys who don't have adequate coverage will not be able to take advantage of it until offline support~~ is ~~added.~~ **still needed.**
- **Removed paragraph:** ~~11. Hardware-dependent performance: Latency figures were tested on one laptop with an NVIDIA GPU and are therefore indicative.~~

### 8.8 Risk Register Revisited

- **Changed:** ~~In~~ **Eight risks were listed in** the Phase 2 ~~report eight risks were listed.~~ **report; their status at the end of Phase 3 is given in Table 8.5.**

### 8.9 Overall Assessment

- **Changed:** ~~Our~~ **The** system passes **all of its** automated tests and ~~gets~~ **degrades** gracefully ~~degraded in case of failure of~~ **when** external ~~services. The major drawbacks of the system~~ **services fail. Its main weaknesses** are on the data ~~side;~~ **side:** the set of new images used ~~for evaluation of~~ **to evaluate** the classifier is small, the Kannada output has not been formally reviewed by native ~~speakers~~ **speakers,** and no ~~tests are based on~~ **automated test uses** real field photographs.

### CONCLUSION AND FUTURE WORK

- **Changed:** PlantIQ started ~~initially~~ as four separate ~~modules. It concludes it~~ **modules and ends Phase 3** as a unified ~~pipe~~ **pipeline** for coffee **growers:**
- **Changed:** ~~farmers:~~ **Step 1: take a photograph of the leaf.**
- **Changed:** Step ~~1: take~~ **2: receive** a ~~photograph of the leaf~~ **treatment plan based on trusted text and current weather.**
- **Changed:** Step ~~2: provide a treatment plan based on trusted text and current weather~~ **3: ask follow-up questions in the grower's own language.**
- **Changed:** Step ~~3: ask follow up questions in~~ **4: offer** the ~~farmers' native language~~ **harvest directly to buyers.**
- **Removed paragraph:** ~~Step 4: deliver the harvest directly to the buyers.~~

### 9.1 Summary of Work Carried Out

- **Added paragraph:** The achievement of each module is summarised in Table 9.1.

### 9.2 Plan of Work Across the Capstone Phases

- **Added paragraph:** The work carried out in each phase of the capstone is shown in Table 9.2.

### 9.3 Key Takeaways

- **Heading:** `9.3 Take Away` → `9.3 Key Takeaways`
- **Changed:** Grounding plus checking is ~~more safe~~ **safer** than ~~grounding. The~~ **grounding alone. Retrieval keeps the** language model ~~is kept near~~ **close to** the ~~source by retrieval~~ **source,** and the dosage audit provides a low-cost check on one of the most serious types of ~~error -~~ **error:** the wrong quantity. This does not guarantee ~~this~~ **that the** advice is ~~safe. It enhances the credibility of~~ **safe, but it makes** the advice ~~while encouraging greater~~ **more credible and invites closer** scrutiny ~~compared to~~ **than** an unchecked response.
- **Changed:** Language support is a design ~~problem and~~ **problem,** not a translation add-on. By detecting the ~~script and then~~ **language,** searching in English and writing the answer in Kannada, a ~~whole model call~~ **separate translation step** was removed and the Kannada path became part of the product. ~~Importing~~ **Adopting** a local speech model also played an important ~~role as~~ **role, because** it ~~decreased~~ **reduced the** reliance on connectivity and quotas.
- **Changed:** Tests change what is built. Several of the most useful improvements of this phase, from the cache ~~salt~~ **key** to the percent-sign fix to the empty-reply guard, were found by tests written to prove something else. A **fast** suite **meant** that ~~runs in under two minutes meant~~ it was run constantly, and it ~~let~~ **allowed** four modules to be integrated without the fear that usually comes with ~~it.~~ **integration.**

### 9.4 What Remains Uncertain

- **Changed:** The classifier is weaker on unseen field photographs than on its validation set, and **the** automated tests do not use real field images. The Kannada pipeline relies on published speech accuracy and has not been reviewed by native speakers. The advisory has been ~~exercised~~ **tested automatically** and ~~tested~~ **benchmarked,** but **it** has not been re-evaluated by an agronomist since Phase 2. ~~And the~~ **The** field feedback, while positive, comes from an initial and informal round. These are the key areas ~~that would~~ **to** be ~~prioritized~~ **prioritised** for improvement.

### 9.6 Reasons for These Upgrades

- **Changed:** Offline first. Most ~~of the~~ coffee plantations are scattered ~~over valleys. The~~ **across valleys, so the** biggest real-world obstacle ~~to use~~ is ~~created by~~ **the need for a network connection, which** a model ~~that is located~~ **running** on the ~~phone.~~ **phone removes.** A conflict-free replicated data type (CRDT) approach ~~allows~~ **lets** the phone and **the** server ~~to synch~~ **merge** edits made offline, so **that** neither side's ~~change will be~~ **changes are** lost, and ~~reducing~~ **converting** the ~~data size~~ **model** to ~~be only~~ INT8 reduces ~~this amount considerably..~~ **its size considerably.**
- **Changed:** Graph-based reasoning. ~~There are frequently many 'restrictions' associated with a~~ **A** grower's ~~'real questions':~~ **real questions often carry several restrictions,** for ~~instance, what~~ **instance which** fungicide can be used on a specific cultivar ~~when blossoms are being rained on by rain just outside the bounds of~~ **during blossom showers near** a ~~stream? That~~ **stream. Answering them** requires ~~some link making—some connecting~~ **connections** between a disease, its ~~control,~~ **control and** the restrictions on ~~those~~ **that control, which a knowledge graph represents directly and flat passage retrieval handles less reliably.**
- **Changed:** Leaf ~~Sought out~~ **wetness:** measured, not ~~modeled conditions.~~ **modelled.** The length of time **that** leaves ~~remain~~ **stay** wet is an important factor in the development of rust ~~disease~~ and is not easily ~~determined~~ **estimated** from regional ~~weather conditions.~~ **weather.** On-farm sensors would ~~enable~~ **allow** the favourability score to be ~~used~~ **computed** for the estate ~~and not~~ **rather than for** the nearest weather grid cell.
- **Changed:** Closing the sale. ~~It is currently up to the "contact the grower" point that~~ **At present** the marketplace ~~reaches. The integration~~ **reaches only the point of contacting the grower. Integration** with **the** Open Network ~~For~~ **for** Digital ~~Commerce and~~ **Commerce, with** escrow payments **held** until delivery and moisture ~~inspection~~ **inspection,** would enable a grower to trade within the app and ~~access~~ **reach** buyers outside ~~of~~ the ~~district..~~ **district.**

### 9.7 Timeline

- **Added paragraph:** The planned horizon for these upgrades is shown in Table 9.4.

### 9.8 Near-Term Steps

- **Changed:** ~~1. Include~~ **Add** a ~~warm up~~ **warm-up** call at start-up to ~~prevent~~ **avoid** the ~~cold start~~ **cold-start** delay on the ~~initial~~ **first** scan.
- **Changed:** ~~2.~~ Gather authentic field photographs, and record per-class precision and recall on ~~them~~ **them.**
- **Changed:** ~~3. Research to see if there is a correlation between~~ **Study whether** the model's confidence ~~and the accuracy level of the model,~~ **matches its accuracy,** and adjust the gate accordingly.
- **Changed:** ~~4.~~ Re-score **a** new sample of advisories, and have native speakers ~~read~~ **review** the Kannada output.
- **Changed:** ~~5. Pilot~~ **Run a structured pilot** with more growers and ~~buyers using a structured design and record~~ **buyers, recording** task completion and time on ~~task..~~ **task.**

### 9.9 Closing Remark

- **Changed:** **A grower is guided by** PlantIQ ~~takes a grower~~ from a sick leaf to an informed treatment decision, which should always be confirmed with an agronomist, and on to a direct sale, in the grower's own language. The project's usefulness is derived from the combined contribution of all these components rather than from any single component individually.

### REFERENCES

- **Changed:** ~~[1] Dr.~~ **S.** Selva ~~Kumar S., Imadh Ajaz~~ **Kumar, I. A.** Banday, ~~Vibha Venkatesh~~ **V. V.** Shanbhag, ~~Afifah Khan Mohammed Ajmal~~ **A. K. M. A.** Khan and ~~Manikantha~~ **M.** Gada, "Overcoming LLM ~~Challenges Using RAG-Driven Precision~~ **challenges using RAG-driven precision** in ~~Coffee Leaf Disease Remediation," IEEE International Conference on~~ **coffee leaf disease remediation," in Proc. Int. Conf.** Emerging Technologies in Computer ~~Science, 2024.~~ **Science for Interdisciplinary Applications (ICETCS), Bengaluru, India, 2024, doi: 10.1109/ICETCS61022.2024.10543859.**
- **Changed:** ~~[2]~~ X. ~~Zhao et al.,~~ **Zhao, B. Chen, M. Ji, X. Wang, Y. Yan, J. Zhang, S. Liu, M. Ye and C. Lv,** "Implementation of ~~Large Language Models~~ **large language models** and ~~Agricultural Knowledge Graphs~~ **agricultural knowledge graphs** for ~~Efficient Plant Disease Detection,"~~ **efficient plant disease detection,"** Agriculture, vol. 14, no. 8, ~~2024.~~ **p. 1359, 2024, doi: 10.3390/agriculture14081359.**
- **Changed:** ~~[3] A.~~ K. S. ~~et al.,~~ **Anudeep, K. M. Prajwal, H. Sireesh Gowda, G. N. Venkatesh Prasad and G. Jagadamba,** "Coffee ~~Leaf Disease Detection Using Convolution Neural Network,"~~ **leaf disease detection using convolution neural network,"** Grenze ~~International Journal of Engineering and Technology,~~ **Int. J. Eng. Technol., vol. 10, no. 2, Jun.** 2024.
- **Changed:** ~~[4]~~ R. ~~Sapkota et al., "Multi-Modal~~ **Sapkota, R. Qureshi, M. U. Hadi, S. Z. Hassan, F. Sadak, M. Shoman, M. Sajjad, F. A. Dharejo, A. Paudel, J. Li, Z. Meng, J. Shutske and M. Karkee, "Multi-modal** LLMs in ~~Agriculture:~~ **agriculture:** A ~~Comprehensive Review," IEEE Transactions on Automation Science and Engineering,~~ **comprehensive review," preprint,** 2024.
- **Changed:** ~~[5]~~ N. ~~Singh et al.,~~ **Singh, J. Wang'ombe, N. Okanga, T. Zelenska, J. Repishti, Jayasankar G K, S. Mishra, R. Manokaran, V. Singh, M. I. Rafiq, R. Gandhi and A. Nambi,** "Farmer.Chat: Scaling ~~AI-Powered Agricultural Services~~ **AI-powered agricultural services** for ~~Smallholder Farmers," ACM Proceedings,~~ **smallholder farmers," arXiv preprint arXiv:2409.08916,** 2024.
- **Changed:** ~~[6]~~ C. S. Santhosha and K. K. Umesh, "An ~~Ensemble Approach~~ **ensemble approach** for ~~Coffee Crop Yield Prediction Based~~ **coffee crop yield prediction based** on ~~Agronomic Factors,"~~ **agronomic factors,"** ASEAN ~~Engineering Journal,~~ **Eng. J.,** vol. 13, no. 3, **pp. 29-38, 2023, doi: 10.11113/aej.V13.18846.**
- **Changed:** ~~2023. [7]~~ S. ~~Patil et al.,~~ **Patil, J. Devasia, G. Daniel and N. Surya Prakash Rao,** "Influence of ~~Elevation~~ **elevation** and ~~Rainfall~~ **rainfall** on ~~Leaf Growth, Bean Characteristics~~ **leaf growth, bean characteristics** and ~~Yield Components~~ **yield components** of ~~Coffee Under Changing Climatic Conditions~~ **arabica and robusta coffee under changing climatic conditions** in ~~Karnataka,~~ **Karnataka state,** India," ~~Journal of~~ **J.** Plantation Crops, vol. 50, no. 2, pp. 78-84, ~~2022.~~ **2022, doi: 10.25081/jpc.2022.v50.i2.7981.**

### DEFINITIONS, ACRONYMS AND ABBREVIATIONS

- **Added paragraph:** The terms, acronyms and abbreviations used in this report are defined in Table A.1.

### USER MANUAL

- **Changed:** ~~A~~ **The following** step-by-step walkthrough was used for the ~~demonstration, assuming access to~~ **demonstration. It assumes** a mobile **phone with an internet connection, or a web browser for the web version.**
- **Removed paragraph:** ~~phone with an internet connection or a web browser for the web-based version.~~

### B.1 Sign In or Register

- **Heading:** `B.1 Sign in or register` → `B.1 Sign In or Register`
- **Changed:** ~~Click on~~ **Open** the app and ~~utilize~~ **use** the Sign In / Register screen. New users ~~click~~ **tap** Register and ~~register~~ **create an account** with a username (or email) and a password, while returning users sign in with the same username and password. An account keeps scans, chats and listings together and private from other users.

### B.2 Scan a Leaf

- **Heading:** `B.2 Scan a leaf` → `B.2 Scan a Leaf`
- **Changed:** ~~Select~~ **Take** a ~~good~~ **clear** picture of ~~a leaf that is damaged,~~ **the affected leaf,** preferably ~~taken~~ in natural light ~~on~~ **against** a plain ~~background~~ **background,** with the leaf ~~occupying~~ **filling** most of the frame. The app ~~will return~~ **returns** the most plausible condition and a confidence value. If the confidence ~~level~~ is ~~less than 75 percent,~~ **below 75%,** the app does not ~~identify any~~ **name a single** disease and provides more general ~~instructions. If not, click on~~ **guidance; in that case, take** the picture again or consult an agronomist.

### B.3 Get Advice

- **Heading:** `B.3 Get advice` → `B.3 Get Advice`
- **Changed:** The advice screen ~~will have~~ **shows** the diagnosis and the current weather at ~~user~~ **the user's** location; ~~give permission~~ **allow access** to ~~use~~ **the** location if the weather ~~needs to~~ **should** be ~~factored in. Advice~~ **taken into account. The advice is drawn** from **the** CCRI text. If ~~a~~ **every** chemical ~~dosage~~ **dose in the advice** is ~~mentioned~~ **found** in the source ~~text it~~ **text, the advisory** is marked as ~~VERIFIED, and it is marked CAUTION~~ **verified;** if ~~it~~ **any dose** is not ~~mentioned. Use CAUTION~~ **found, a caution is shown with the unverified quantities. Treat the caution** as a reminder to ~~always~~ read the product label and consult ~~with~~ an expert before spraying.

### B.4 Ask in Kannada

- **Changed:** ~~Make~~ **When opening the chat, make** sure **that** the ~~leaf, the user wants~~ **leaf** the assistant ~~to~~ **should** know about is shown ~~in~~ **on** the scan ~~screen when opening the chat.~~ **screen.** Type ~~using~~ **in** Kannada, English or a combination of ~~both~~ **both,** or use the microphone. If **the question is** written in Kannada script, the reply ~~will be~~ **is** returned in Kannada. The assistant remembers the last 8 messages.

### B.5 List and Sell

- **Heading:** `B.5 List and sell` → `B.5 List and Sell`
- **Changed:** ~~If user wishes to~~ **To** sell a lot, **prepare** a listing ~~will be prepared~~ that includes the coffee variety, the quantity, **the** price per ~~kilogram,~~ **kilogram** and ~~user~~ **a** contact ~~number~~ **number,** along with ~~pictures with attention-grabbing captions.~~ **captioned photos.** Listings are ~~restricted~~ **sorted** by distance, filtered by price and searched by keyword. ~~They will guide buyers~~ **Buyers can open directions** to the farm in Maps, call ~~them~~ **the grower** or ~~launch~~ **start** a WhatsApp chat with a ~~pre-formulated~~ **pre-written** message.

### AUTOMATED TEST CATALOGUE

- **Changed:** The ~~48~~ **373** tests are grouped by ~~file and area. The descriptions below say~~ **type in Table C.1, which also states** what each group checks.

### TEAM CONTRIBUTIONS

- **Added paragraph:** The responsibilities of each team member are listed in Table D.1.


## F. Table content changes

Each new table row is compared with the closest row of the original tables. Rows not listed are unchanged. Header rows of the Table of Contents, List of Figures and List of Tables are regenerated automatically and are not listed.

### Table 1.1: The four modules of PlantIQ

- 2. Advisory engine | Produce grounded treatment advice with a dosage check | ~~BGE-base-en,~~ **bge-m3 (BGE-base-en on CPU),** FAISS, BM25, ~~cross- encoder,~~ **cross-encoder,** Gemini, Open-Meteo
- 3. Chatbot | Answer follow-up questions by voice or text in Kannada or English | IndicConformer, Whisper, Gemini Audio, ~~Unicode pre-router~~ **language router**

### Table 1.2: Where Phase 2 ended and where Phase 3 stands

- Retrieval | Dense FAISS search, MiniLM embeddings (384-d), top 5 | **bge-m3 (1024-d;** BGE-base-en ~~(768-d),~~ **on CPU),** FAISS plus BM25, RRF fusion, cross-encoder rerank, top 3
- Weather input | Simulated values | Live data **and a three-day forecast** from Open-Meteo; nothing invented when ~~GPS~~ **location** is missing
- Kannada text | Post-translation layer planned | ~~Script pre-router and an~~ **Language router writes one** English search ~~query; no separate translation call~~ **question; reply in Kannada script**
- Testing | Per-module checks and a manual evaluation | ~~48~~ **373** automated ~~pytest tests,~~ **tests (pytest, Vitest, Playwright),** all passing

### Table 1.3: Review suggestions and progress shown

- 5 | Streamline the integration flow | High | CNN, RAG, chatbot ~~a~~ **and market** discovery connected; ~~b~~ **backend wired to** frontend; end-to-end pipeline working

### Table 3.1: Summary of the surveyed papers

- [3] CNN for coffee leaves | ~~GoogLeNet~~ **GoogLeNet-style CNN** on about 8,500 images | CNNs work for coffee diseases | Weaker on messy field photos
- [5] Farmer.Chat | RAG chatbot on WhatsApp and Telegram | Reach farmers on familiar apps | ~~Text only; no~~ **No coffee-specific** image diagnosis or market

### Table 4.1: Functional requirements

- FR-2.4 | Fall back from Gemini to Groq, and then to **an offline guide with** the retrieved text, when a language model is unavailable.
- FR-4.1 | Create crop listings with price, quantity and phone number, validated ~~b~~ **before saving.**
- FR-4.3 | Sort listings by distance from the buyer, and filter by ~~price~~ **price, variety, distance** and keyword.

### Table 4.3: Data assets

- Composite ~~leaf- image~~ **leaf-image** set | CNN training and evaluation | JMuBEN, PlantVillage, PlantDoc | Five classes in the final model
- CCRI text passages | Hybrid retrieval | Central Coffee Research Institute **and research articles** | ~~Dense~~ **931 passages; dense** (FAISS, ~~768-d)~~ **1024-d)** and sparse (BM25) indexes
- Live microclimate | Favourability score and prompt | Open-Meteo | Temperature, humidity, ~~rainfall;~~ **rainfall, three-day forecast;** never fabricated
- Users, cache, chats, listings | Whole application | Created by the app | SQLAlchemy models; ~~images as Base64,~~ photos as ~~JSON~~ **sanitised files**

### Table 4.4: How the objectives were met by the end of Phase 3

- Leaf classifier | Met: five classes, about 90% on ~~validation and~~ **validation,** about 80% on new ~~leaves,~~ **leaves and 97.9% in leak-free cross-validation;** 75% confidence gate | Sections 6.1, 8.2
- Kannada and English chatbot | Met: three-tier speech chain, ~~script pre-router~~ **language router** and context fusion | Section 6.3
- Live environmental data | Met for temperature, ~~humidity~~ **humidity, rainfall** and ~~rainfall;~~ **a three-day forecast;** soil ~~and elevation~~ **data** not part of the build | Section 6.2
- Automated testing | Met: ~~48~~ **373** of ~~48~~ **373** tests pass | Sections 6.5, 8.1
- Resilience to service failure | Met for the language-model and ~~speech- recognition~~ **speech-recognition** fallbacks | Sections 6.2, 6.3, 8.4

### Table 5.1: Contents and role of each layer

- 1. Client and inputs | Mobile APK and web ~~PWA~~ **app** (Capacitor 7); estate GPS; leaf photo upload; voice or text query in Kannada or English; crop lot details and photos | Collects everything the grower provides
- 2. Perception and processing | Microclimate service ~~(Open-Meteo~~ **(Open-Meteo, infection-risk level** and ~~spore- risk score);~~ **spray window);** Module 1 CNN; speech-to-text with the language ~~pre-router;~~ **router;** Module 4 marketplace | Turns raw inputs into structured signals: weather risk, a diagnosis with confidence, a transcribed query, a listing
- 3. AI reasoning and advisory | Module 2 hybrid RAG; LLM advisory (Gemini with Groq ~~failover);~~ **failover and an offline guide);** Module 3 chatbot | Combines the signals with retrieved knowledge and writes a reply in the right language
- 4. Storage and outcomes | FAISS knowledge base; relational database for users, cache, chats and listings; **media store;** bilingual reply; Maps and WhatsApp hand-offs | Persists state and delivers the result or the next action

### Table 5.2: Module 1 design parameters

- **New row:** Leak-free accuracy | 97.9% | Five-fold cross-validation on JMuBEN; macro-F1 0.970

### Table 5.3: Module 2 design parameters

- Dense embeddings | ~~BGE-base-en, 768~~ **bge-m3, 1024** dimensions **(BGE-base-en, 768, on a CPU)** | Meaning-based ~~matching~~ **matching, including Kannada**
- Candidates per method | ~~15~~ **20** | Wide enough to catch the right passage
- Fusion constant | k = 60 | Standard ~~reciprocal-ra~~ **reciprocal-rank fusion constant**
- Language model | Gemini 2.5 Flash, Groq as ~~failover~~ **failover, offline guide last** | Quality first, resilience second

### Table 5.4: Module 3 key figures

- Script detection time **(fallback router)** | Under 1 ms (0.08 ms measured)
- **New row:** Chat turn without the language model | 0.22 s (median)

### Table 5.5: Module 4 features

- Photo galleries | ~~Multiple~~ **Up to eight** photos with captions, stored as ~~JSON~~ **sanitised files** | Buyers can judge a lot before calling
- **New row:** Unit normalisation | Quantities in kg and prices in Rs./kg, computed on the server | Lots sold in bags, quintals or tonnes can be compared
- Filters | Price ~~slider~~ **range, variety, distance** and keyword search | Quick narrowing of results

### Table 6.3: Test methods

- Unit ~~and functional~~ (per ~~module)~~ **module, pytest)** | ~~25~~ **162** | Isolates faults to one module before they compound
- **New row:** Functional journeys (multi-step, through the API) | 3 | Checks complete user journeys across modules
- Integration ~~(end to end~~ **(API and database** via the FastAPI test client) | ~~7~~ **71** | Modules pass data to each other, so the pipeline must be verified as a whole
- Security | ~~8~~ **59** | The app handles user accounts and gives chemical spray advice, where a wrong answer can cause real harm
- Performance (hardware-dependent) | ~~8~~ **10** | ~~Latency~~ **Latency, load** and concurrency checks; figures depend on test hardware
- **New row:** Real model | 4 | Loads the deployed CNN weights and the bge-m3 index
- **New row:** Frontend unit and component (Vitest) | 52 | Checks screens, components and the English and Kannada dictionaries
- **New row:** End-to-end UI (Playwright, Pixel 7) | 12 | Runs complete journeys in a phone-sized browser
- Total | ~~48~~ **373** | 

### Table 7.1: Technology used in each module

- Module 1: leaf pathology | ~~PyTorch,~~ **PyTorch 2.7.1,** ResNet-50, CUDA, SHA-256 result cache, relational database
- Module 2: advisory engine | **bge-m3 embeddings (1024-d;** BGE-base-en ~~embeddings (768-d),~~ **on CPU),** FAISS, rank_bm25, ~~MiniLM cross- encoder,~~ **bge-reranker-v2-m3 (MiniLM on CPU),** Gemini 2.5 Flash, ~~a 120B model~~ **gpt-oss-120b** on Groq, Open-Meteo API
- Module 3: chatbot | IndicConformer-600M, Svarah Whisper, Groq Whisper, Gemini Audio, **language router with a** Unicode ~~regular expressions, Base64~~ **fallback,** image ~~storage~~ **files linked to chat threads**
- Module 4: marketplace | FastAPI, SQLAlchemy, Haversine distance, **unit normalisation,** Capacitor Android intents, Google Maps URLs, WhatsApp deep links (wa.me)
- Application and tests | **React 18 and TypeScript,** FastAPI, SQLAlchemy over ~~PostgreSQL,~~ **PostgreSQL or SQLite,** Capacitor 7, pytest, FastAPI TestClient (Starlette and HTTPX), ~~Pillow~~ **Pillow, Vitest, Playwright**

### Table 7.2: Individual contribution towards testing

- Member | Module | ~~Test file~~ **Tests** and responsibility
- Mohammed Ayaan | CNN | ~~test_cnn.py (7 tests): weights,~~ **Module 1 tests (41): weights and SHA-256 check,** architecture, preprocessing, softmax sums to 100%, ~~SHA-256~~ **result** cache, corrupted input, 75% confidence ~~gate~~ **gate, real-model checks**
- Jeel Nada | RAG **and environment** | ~~test_rag.py (9 tests):~~ **Module 2 tests (54):** zero-mock weather, ~~spore-risk logic,~~ **risk level and spray window,** FAISS and BM25, RRF, **rerank and** sigmoid bounds, dosage audit, ~~end- to-end~~ **end-to-end** advisory
- Nidhi N | Chatbot and marketplace | ~~test_chatbot.py (5 tests):~~ **Module 3 tests (49):** Kannada and English routing, **history,** GPS parsing, thread and image ~~persistence. test_market.py (4 tests): listing~~ **persistence, speech chain. Module 4 tests (73): listings** with photos, **unit normalisation,** Haversine, WhatsApp and tel: URLs, filters
- **New row:** All three | Platform, integration and security | Platform tests (143) and the functional and performance tests (13): accounts, security, app shell, user journeys and latency, each member testing the endpoints of their own module

### Table 7.3: Test tools and their role

- **New row:** Vitest | Frontend unit and component tests
- **New row:** Playwright | End-to-end tests in a Pixel 7 browser

### Table 8.1: Expected and actual results

- Automated test pass rate | All pass | ~~48~~ **373** of ~~48~~ **373** | Met
- **New row:** Distance sort over 500 listings | Under 1.5 s | Within budget | Met

### Table 8.2: Measured response times

- Script detection in the ~~pre-router~~ **fallback router** | 0.08 ms | A regular-expression check
- CNN ~~warm~~ inference **on the GPU** | ~~14.2~~ **5.3** ms | ~~After~~ **Median, after** the GPU is initialised
- **New row:** CNN inference on the CPU | 54.9 ms | Median
- **New row:** Chat turn without the language model | 0.22 s | Median: CNN, routing, weather and retrieval
- **New row:** Hybrid retrieval | About 0.4 s | Dense, BM25, fusion and rerank
- **New row:** Complete advisory | About 6 s | Dominated by language-model generation

### Table 8.3: Design choices compared with typical alternatives

- ~~Our~~ **PlantIQ** approach | Typical alternative | Outcome
- ~~Regex pre-router~~ **Language router** and English search query | Neural translation of Kannada | ~~Script~~ **One short routing call (0.08 ms script** check ~~takes 0.08 ms;~~ **as fallback);** no ~~separate~~ translation ~~call~~ **of the answer**
- SHA-256 result cache | Re-running the CNN on every scan | 0.85 ms cache lookup against ~~14.2~~ **5.3** ms inference per repeat

### Table 8.4: Advisory and chatbot benchmark results

- **New row:** Measure | PlantIQ | Dense-only pipeline | No retrieval
- **New row:** Evidence in top 3 passages (75 questions) | 0.867 | 0.500 | n/a
- **New row:** Evidence in top 3 passages (21 Kannada questions) | 0.905 | 0.095 | n/a
- **New row:** Correct answers (54 English questions) | 0.944 | 0.824 | 0.611
- **New row:** Answers with an unsupported dose | 0.0% | 0.0% | 20.4%
- **New row:** Conversations with the expected behaviour (43) | 43 | 15 | n/a
- **New row:** Correct chatbot answers (29 knowledge questions) | 0.91 | 0.38 | n/a

### Table 8.5: Status of the Phase 2 risks

- R02 | Language-model rate limits or outages | Mitigated: Gemini to Groq to ~~CCRI fallback;~~ **offline guide;** the quota limit did occur in testing and the fallbacks worked
- R06 | Spatial queries degrading with scale | Changed: proximity computed with Haversine in the application; **500 listings sorted within 1.5 s;** to be revisited if listing volume grows large
- R08 | Report similarity above the permitted limit | Managed: report written in ~~our own~~ **original** words; similarity check to be run at the library before submission

### Table 9.1: What each module achieved

- CNN | ResNet-50 classifies five leaf conditions, with a 75% confidence gate and a SHA-256 cache that skips repeat ~~inference~~ **inference; 97.9% accuracy in leak-free cross-validation**
- RAG | Dense, BM25, RRF and cross-encoder retrieval with live microclimate ~~input~~ **input, a spray window** and a dosage audit that flags chemical quantities missing from the CCRI source text
- Chatbot | Voice and text in Kannada, Kanglish and English, with a ~~lightweight pre- router~~ **language router, conversation memory** and scan-to-chat context
- Marketplace | Direct grower-to-buyer listings with photo galleries, **unit normalisation,** Haversine proximity sorting, Maps navigation and one-tap call and WhatsApp
- Whole system | Integrated end to end, with ~~48~~ **373** of ~~48~~ **373** automated tests passing across modules, ~~integration~~ **integration, security** and ~~security~~ **the frontend**

### Table 9.2: Progress from Phase 1 to Phase 3

- **New row:** Phase 3 | Modules rebuilt and integrated behind one backend; five-class CNN; hybrid retrieval with live weather and dosage audit; Kannada language router and three-tier speech chain; automated test suite of 373 tests; leak-free classifier evaluation; retrieval and chatbot benchmarks; initial field feedback

### Table A.1: Terms used in this report

- **New row:** bge-m3 | A multilingual text-embedding model used for dense retrieval
- Zero-mock policy | ~~Our~~ **The** rule that weather is never fabricated when **the** location is missing

### Table C.1: Test groups

- **New row:** Backend unit (pytest) | 162 | Model weights and head, preprocessing, softmax, cache, confidence gate; weather rules, retrieval indexes, RRF, rerank, dosage audit; language routing, chat memory; unit normalisation, Haversine, links; schemas, password and token handling
- ~~test_integrated.py~~ **Integration (FastAPI test client)** | ~~7~~ **71** | Authentication; scan to CNN to RAG advisory; cache hit; ~~scan- to-chat~~ **scan-to-chat** hand-off; **chat threads and images;** marketplace ~~to Maps~~ **listings, filters** and ~~WhatsApp~~ **reports**
- **New row:** Functional journeys | 3 | Complete multi-step journeys through the API, from sign-up to scan, chat and listing
- ~~test_security.py~~ **Security** | ~~8~~ **59** | Authentication and tokens; cross-user isolation (403); unauthorised access (401); SQL injection; cross-site scripting; **upload guard;** dosage guardrail; ~~corrupted uploads~~ **rate limits**
- ~~Performance~~ **Non-functional** | ~~8~~ **10** | ~~Latency~~ **Latency, load** and concurrency checks, including 10 parallel ~~workers;~~ **workers and distance sorting over 500 listings;** results depend on the test hardware
- **New row:** Real model | 4 | Deployed CNN weights on one sample photograph per class and the bge-m3 retrieval index
- **New row:** Frontend unit and component (Vitest) | 52 | Screens, components, safe rendering of model text and parity of the English and Kannada dictionaries
- **New row:** End-to-end UI (Playwright) | 12 | Complete journeys in a Pixel 7 browser, including language switching and accessibility checks
- Total | ~~48~~ **373** | All ~~passing; suite runs in about 103 seconds~~ **passing at their last run**

### Table D.1: Responsibilities of each team member

- Mohammed Ayaan | PES2UG23AM058 | CNN model, ResNet-50 fine-tuning, inference and cache; **Module 1** tests ~~in test_cnn.py~~
- Jeel Nada | PES2UG23CS357 | Hybrid RAG engine, knowledge base and indexes, LLM integration, dosage audit; **Module 2** tests ~~in test_rag.py~~
- Nidhi N | PES2UG23CS384 | Chatbot, speech chain and ~~pre-router,~~ **language router,** marketplace; **Module 3 and Module 4** tests ~~in test_chatbot.py and test_market.py~~
- All three |  | Integration, security ~~testing (test_integrated.py and test_security.py),~~ **testing,** report and demonstration

