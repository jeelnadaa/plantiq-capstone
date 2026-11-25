"""Creates content_old_*.txt: the v3 text with every latest-project data update reverted to the
original report's data. Language, grammar, passive voice and structure fixes are kept.
Each replacement must match exactly once, so a stale pattern fails loudly."""
import re

R = {1: [], 2: [], 3: []}

# ---------------------------------------------------------------- chapters 1-3
R[1] += [
    ("| 2. Advisory engine | Produce grounded treatment advice with a dosage check | bge-m3 (BGE-base-en on CPU), FAISS, BM25, cross-encoder, Gemini, Open-Meteo |",
     "| 2. Advisory engine | Produce grounded treatment advice with a dosage check | BGE-base-en, FAISS, BM25, cross-encoder, Gemini, Open-Meteo |"),
    ("| IndicConformer, Whisper, Gemini Audio, language router |", "| IndicConformer, Whisper, Gemini Audio, Unicode pre-router |"),
    ("| bge-m3 (1024-d; BGE-base-en on CPU), FAISS plus BM25, RRF fusion, cross-encoder rerank, top 3 |",
     "| BGE-base-en (768-d), FAISS plus BM25, RRF fusion, cross-encoder rerank, top 3 |"),
    ("| Live data and a three-day forecast from Open-Meteo; nothing invented when location is missing |",
     "| Live data from Open-Meteo; nothing invented when GPS is missing |"),
    ("| Language router writes one English search question; reply in Kannada script |",
     "| Script pre-router and an English search query; no separate translation call |"),
    ("| 373 automated tests (pytest, Vitest, Playwright), all passing |", "| 48 automated pytest tests, all passing |"),
    (" A later leak-free five-fold evaluation on the public JMuBEN images, also reported in Section 8.2, measured an accuracy of 97.9%.", ""),
    ("| [3] CNN for coffee leaves | GoogLeNet-style CNN on about 8,500 images |", "| [3] CNN for coffee leaves | GoogLeNet on about 8,500 images |"),
    ("| No coffee-specific image diagnosis or market |", "| Text only; no image diagnosis or market |"),
]

# ---------------------------------------------------------------- chapters 4-6
R[2] += [
    ("# Provide a chatbot that can take voice and text input in Kannada and English, recall",
     "# Provide a chatbot that can hear and speak in Kannada and English, recall"),
    ("| Fall back from Gemini to Groq, and then to an offline guide with the retrieved text, when a language model is unavailable. |",
     "| Fall back from Gemini to Groq, and then to the retrieved text, when a language model is unavailable. |"),
    ("| Sort listings by distance from the buyer, and filter by price, variety, distance and keyword. |",
     "| Sort listings by distance from the buyer, and filter by price and keyword. |"),
    ("Two sets of evaluations were reported for Phase 3.", "Two sets of evaluations are reported in this report."),
    (" A third, leak-free evaluation was added later, because an audit found that the 58,549 JMuBEN files come from only 861 distinct leaf patches; in this evaluation every copy of a patch stays on the same side of each fold.", ""),
    ("The fast automated tests do not use real images.", "The automated tests do not use real images."),
    (" Four separate real-model tests load the deployed weights and classify one sample photograph of each class.", ""),
    (", together with research articles on coffee diseases, pests and nutrition (14 PDF documents and 931 passages in all).", "."),
    ("The dense index is a FAISS index of 1024-dimensional bge-m3 embeddings (768-dimensional BGE-base-en embeddings when no GPU is available);",
     "The dense index is a FAISS index of 768-dimensional BGE-base-en embeddings;"),
    ("Each passage carries a topic tag, which lets the pipeline prefer retrieved text on the disease that the classifier has named.",
     "Each passage carries a disease tag, which lets the pipeline filter the retrieved text to the disease that the classifier has named."),
    ("provides the temperature, humidity, rainfall, elevation and a three-day forecast for a given coordinate.",
     "provides the temperature, humidity and rainfall for a given coordinate."),
    ("All the data written by the application is stored in a relational database (PostgreSQL, or SQLite for zero-configuration deployments) through SQLAlchemy: user accounts, cached scan results, marketplace listings and chats. Listing photos and chat images are stored as sanitised image files, with their captions and paths in the database, so that they survive page refreshes without bloating the database rows.",
     "All the data written by the application is stored in a relational store through SQLAlchemy: user accounts, cached scan data, marketplace listings (with photo galleries stored as JSON) and chats (with leaf images stored as Base64, so that they survive page refreshes without being lost)."),
    ("| Central Coffee Research Institute and research articles | 931 passages; dense (FAISS, 1024-d) and sparse (BM25) indexes |",
     "| Central Coffee Research Institute | Dense (FAISS, 768-d) and sparse (BM25) indexes |"),
    ("| Temperature, humidity, rainfall, three-day forecast; never fabricated |", "| Temperature, humidity, rainfall; never fabricated |"),
    ("| SQLAlchemy models; photos as sanitised files |", "| SQLAlchemy models; images as Base64, photos as JSON |"),
    ("with an NVIDIA RTX 3070 Laptop GPU (CUDA 12) and Python 3.11. The server is a single FastAPI application on top of a relational database. The client is a React web app wrapped for Android using Capacitor 7, so it runs as a web app in a browser or as an installed app.",
     "with an NVIDIA RTX GPU (CUDA 12) and Python 3.11. The server is a single FastAPI application on top of a relational database. The client is a web app wrapped for Android using Capacitor 7, so it runs as a PWA in a browser or as an installed app."),
    ("Weather data is available only at grid level, and soil data is not included.", "Weather data is available only at grid level, and soil data and elevation are not included."),
    ("| Met: five classes, about 90% on validation, about 80% on new leaves and 97.9% in leak-free cross-validation; 75% confidence gate |",
     "| Met: five classes, about 90% on validation and about 80% on new leaves, 75% confidence gate |"),
    ("| Met: three-speech chain", "| Met: three-speech chain"),  # placeholder (no-op guard, removed below)
    ("| Met: three-tier speech chain, language router and context fusion |", "| Met: three-tier speech chain, script pre-router and context fusion |"),
    ("| Met for temperature, humidity, rainfall and a three-day forecast; soil data not part of the build |",
     "| Met for temperature, humidity and rainfall; soil and elevation not part of the build |"),
    ("| Met: 373 of 373 tests pass |", "| Met: 48 of 48 tests pass |"),
    ("| Mobile APK and web app (Capacitor 7);", "| Mobile APK and web PWA (Capacitor 7);"),
    ("Microclimate service (Open-Meteo, infection-risk level and spray window); Module 1 CNN; speech-to-text with the language router;",
     "Microclimate service (Open-Meteo and spore-risk score); Module 1 CNN; speech-to-text with the language pre-router;"),
    ("LLM advisory (Gemini with Groq failover and an offline guide);", "LLM advisory (Gemini with Groq failover);"),
    ("relational database for users, cache, chats and listings; media store; bilingual reply;",
     "relational database for users, cache, chats and listings; bilingual reply;"),
    ("Dense and keyword search each return their top 20 passages, which are fused, reranked with a preference for the diagnosed disease and reduced to the top 3.",
     "Dense and keyword search each return their top 15 passages, which are fused, filtered to the disease and reranked down to the top 3."),
    ("the language router recognises the Kannada script and writes an English search question,",
     "the pre-router recognises the Kannada script and creates an English query for the search,"),
    ("When no language model is available for the advisory, the system answers from an offline guide and the retrieved CCRI text alone.",
     "When no language model is available for the advisory, the system answers from the retrieved CCRI text alone."),
    ("In this configuration, the app reaches the backend through a server address that can be set at run time.",
     "In this configuration, the app reaches the backend through a dynamic IP address."),
    ("| Leak-free accuracy | 97.9% | Five-fold cross-validation on JMuBEN; macro-F1 0.970 |\n", ""),
    ("| Dense embeddings | bge-m3, 1024 dimensions (BGE-base-en, 768, on a CPU) | Meaning-based matching, including Kannada |",
     "| Dense embeddings | BGE-base-en, 768 dimensions | Meaning-based matching |"),
    ("| Candidates per method | 20 |", "| Candidates per method | 15 |"),
    ("| Gemini 2.5 Flash, Groq as failover, offline guide last |", "| Gemini 2.5 Flash, Groq as failover |"),
    ("| Script detection time (fallback router) | Under 1 ms (0.08 ms measured) |", "| Script detection time | Under 1 ms (0.08 ms measured) |"),
    ("| Chat turn without the language model | 0.22 s (median) |\n", ""),
    ("| Up to eight photos with captions, stored as sanitised files |", "| Multiple photos with captions, stored as JSON |"),
    ("| Unit normalisation | Quantities in kg and prices in Rs./kg, computed on the server | Lots sold in bags, quintals or tonnes can be compared |\n", ""),
    ("| Price range, variety, distance and keyword search |", "| Price slider and keyword search |"),
    (" Before this, every upload passes an image guard that checks the file signature and size limits, removes metadata such as GPS coordinates and re-encodes the image as a clean JPEG.", ""),
    (" In the current build, a result is also marked uncertain when a disease is predicted but the best retrieved passage scores below 0.60, so that weak evidence is flagged as well.", ""),
    (" The current build reports the score as a high, moderate or low risk level (high when the rule above holds, moderate when the humidity is at least 65% or it has rained that day) and recommends a spray window from the three-day forecast.", ""),
    ("Dense search uses FAISS over bge-m3 embeddings (BGE-base-en on a CPU) and finds passages that match in meaning. Sparse search uses BM25 and finds passages that match in wording. Each returns its top 20.",
     "Dense search uses FAISS over BGE-base-en embeddings and finds passages that match in meaning. Sparse search uses BM25 and finds passages that match in wording. Each returns its top 15."),
    ("A cross-encoder (bge-reranker-v2-m3 on a GPU, MiniLM on a CPU) reads", "A MiniLM cross-encoder reads"),
    (" Passages on the diagnosed disease receive a small preference of 0.1 for ordering, near-duplicate passages are removed, and the best 3 passages are retained.",
     " The best 3 passages are retained."),
    ("the call goes to a 120B model (gpt-oss-120b) hosted on Groq; if that is also not possible, the system displays an offline guide for the disease together with the retrieved CCRI text.",
     "the call goes to a 120B model hosted on Groq; if that is also not possible, the system displays the retrieved CCRI text directly."),
    (", which check behaviour but are not a substitute for another round of expert review, together with the automated benchmark reported in Section 8.6.",
     ", which check behaviour but are not a substitute for another round of expert review."),
    (" In the current build, the router first asks the language model, in a short JSON-mode call, for the language and one self-contained English search question, and it also receives the last two exchanges so that follow-up questions are understood; the Unicode check is used when the language model is unavailable.", ""),
    (" The transcript is placed in the input box for the grower to correct; it is never sent automatically.", ""),
    ("The chatbot saves the leaf images sent by the user and links them to the user's thread, so that each thread keeps its images. In the current build the images are stored as sanitised files rather than as Base64 strings inside the database, which keeps the database rows small and removes any location metadata from the photos.",
     "The chatbot saves the leaf images sent by the user as Base64 strings in the database and ensures that each user thread keeps its images. This is not a scalable way to store large numbers of images, but it is simple, avoids a separate file store and works at the current scale."),
    ("Each listing can have a gallery of up to eight photos, each with a caption. Because growers trade in different units, the server converts quantities to kilograms and prices to rupees per kilogram, so that lots sold in bags, quintals or tonnes can be compared.",
     "Each listing can have a multi-photo gallery with a caption for each photo. The photos and their captions are stored in JSON format, allowing a variable number of photos with a simple schema."),
    ("The results can be filtered by a price range, variety, minimum lot size, maximum distance and a keyword search, each applied as a database query.",
     "The results can be filtered by a dual-handle price slider and by a keyword search, each applied as a database query."),
    ("an automated suite was created with pytest for the backend, later joined by Vitest and Playwright for the frontend, and it was treated as part of the product.",
     "an automated suite was created using pytest and treated as part of the product."),
    ("Table 6.3 lists the test methods used: unit, functional, integration, security, performance, real-model, frontend and end-to-end tests. Together, 373 tests check",
     "Table 6.3 lists the test methods used: unit and functional testing, integration testing, security testing and performance testing. Together, 48 tests check"),
]
OLD_T63 = """| Method | Tests | Why it is needed |
| Unit and functional (per module) | 25 | Isolates faults to one module before they compound |
| Integration (end to end via the FastAPI test client) | 7 | Modules pass data to each other, so the pipeline must be verified as a whole |
| Security | 8 | The app handles user accounts and gives chemical spray advice, where a wrong answer can cause real harm |
| Performance (hardware-dependent) | 8 | Latency and concurrency checks; figures depend on test hardware |
| Total | 48 | |
"""

# ---------------------------------------------------------------- chapters 7-9 and appendices
R[3] += [
    ("| Module 1: leaf pathology | PyTorch 2.7.1, ResNet-50,", "| Module 1: leaf pathology | PyTorch, ResNet-50,"),
    ("| Module 2: advisory engine | bge-m3 embeddings (1024-d; BGE-base-en on CPU), FAISS, rank_bm25, bge-reranker-v2-m3 (MiniLM on CPU), Gemini 2.5 Flash, gpt-oss-120b on Groq, Open-Meteo API |",
     "| Module 2: advisory engine | BGE-base-en embeddings (768-d), FAISS, rank_bm25, MiniLM cross-encoder, Gemini 2.5 Flash, a 120B model on Groq, Open-Meteo API |"),
    ("| Module 3: chatbot | IndicConformer-600M, Svarah Whisper, Groq Whisper, Gemini Audio, language router with a Unicode fallback, image files linked to chat threads |",
     "| Module 3: chatbot | IndicConformer-600M, Svarah Whisper, Groq Whisper, Gemini Audio, Unicode regular expressions, Base64 image storage |"),
    ("| Module 4: marketplace | FastAPI, SQLAlchemy, Haversine distance, unit normalisation, Capacitor", "| Module 4: marketplace | FastAPI, SQLAlchemy, Haversine distance, Capacitor"),
    ("| Application and tests | React 18 and TypeScript, FastAPI, SQLAlchemy over PostgreSQL or SQLite, Capacitor 7, pytest, FastAPI TestClient (Starlette and HTTPX), Pillow, Vitest, Playwright |",
     "| Application and tests | FastAPI, SQLAlchemy over PostgreSQL, Capacitor 7, pytest, FastAPI TestClient (Starlette and HTTPX), Pillow |"),
    ("equipped with an NVIDIA RTX 3070 Laptop GPU (CUDA 12)", "equipped with an NVIDIA RTX GPU (CUDA 12)"),
    ("one from bge-m3 vectors and another", "one from BGE-base-en vectors and another"),
    ("it falls back to the Groq-hosted model, and finally to the offline guide and the retrieved text.", "it falls back to the Groq-hosted model, and finally to the retrieved text."),
    (' Number words are now also converted to digits, so that "four litres" is audited as "4 L".', ""),
    ("3. D ← top 20 of FAISS_search(bge-m3(q)); S ← top 20 of BM25_search(q)", "3. D ← top 15 of FAISS_search(BGE(q)); S ← top 15 of BM25_search(q)"),
    ("5. C ← passages sorted by score\n6. R ← top 3 of C ranked by Sigmoid(CrossEncoder(q, passage)),\n      +0.1 if tag = disease, near-duplicates skipped",
     "5. C ← passages sorted by score, filtered to tag = disease\n6. R ← top 3 of C ranked by Sigmoid(CrossEncoder(q, passage))"),
    ("8. answer ← Gemini(prompt) ON FAILURE Groq(prompt) ON FAILURE offline guide + text of R", "8. answer ← Gemini(prompt) ON FAILURE Groq(prompt) ON FAILURE text of R"),
    ("The language router asks the language model for the language of the message and one English search question, and falls back to a short regular-expression function over Unicode character ranges. For a Kannada query, the English question is used for retrieval and an instruction to answer in Kannada script is added.",
     "The pre-router is a short regular-expression function over Unicode character ranges. For a Kannada query, it creates an English query for retrieval and adds an instruction to return the answer in Kannada script."),
    ("Leaf images sent in the chat are saved as sanitised files and linked to the thread through SQLAlchemy.", "Leaf images sent in the chat are saved as Base64 strings through SQLAlchemy."),
    ("2. (english_query, target_language) ← Router(text, last 2 exchanges)   // Unicode check as fallback", "2. (english_query, target_language) ← PreRoute(text)   // Unicode script check"),
    ("7. reply ← Gemini(prompt) ON FAILURE Groq(prompt) ON FAILURE offline reply", "7. reply ← Gemini(prompt) ON FAILURE Groq(prompt)"),
    ("8. save turn (and image file) to thread_id; RETURN reply", "8. save turn (and Base64 image) to thread_id; RETURN reply"),
    ("Photos are stored as sanitised files, with their captions in the database.", "Photo galleries are stored as a JSON list of objects with a URL and a caption."),
    ("""2. qty_kg, price_per_kg ← Normalise(quantity, unit, price, price_unit)
3. photos ← up to 8 sanitised image files with captions
4. maps_url ← Maps link from farm latitude and longitude
5. save listing to database
SEARCH:
6. FOR each listing L: L.distance ← Haversine(buyer, L.location)
7. apply price, variety, distance and keyword filters
8. sort listings by distance ascending
9. attach wa.me link with URL-encoded message; RETURN listings""",
     """2. gallery ← JSON list of {url, caption}
3. maps_url ← Maps link from farm latitude and longitude
4. save listing to database
SEARCH:
5. FOR each listing L: L.distance ← Haversine(buyer, L.location)
6. apply price range and keyword filters
7. sort listings by distance ascending
8. attach wa.me link with URL-encoded message; RETURN listings"""),
    ("Pillow generates the synthetic and corrupted images, and Vitest and Playwright test the frontend.", "and Pillow generates the synthetic and corrupted images."),
    ("The integration tests use the FastAPI test client, the data layer runs on SQLAlchemy, and Pillow", "The integration tests use the FastAPI test client, the data layer runs on SQLAlchemy, Pillow"),
    ("| Vitest | Frontend unit and component tests |\n| Playwright | End-to-end tests in a Pixel 7 browser |\n", ""),
    ("**Benefits.** The fast backend suite runs without a GPU, using deterministic fakes for the models, so it was possible to run it after nearly every change.",
     "**Benefits.** The entire suite takes about 103 seconds to finish, so it was possible to run it after nearly every change."),
    ("The fast tests rely on synthetic leaf images", "The tests rely on synthetic leaf images"),
    ("| Automated test pass rate | All pass | 373 of 373 | Met |", "| Automated test pass rate | All pass | 48 of 48 | Met |"),
    ("| Distance sort over 500 listings | Under 1.5 s | Within budget | Met |\n", ""),
    ("The CNN achieved a validation accuracy of 90% and an accuracy of 80% on new leaf images. A later leak-free five-fold cross-validation on the public JMuBEN images measured an accuracy of 97.9% and a macro-F1 of 0.970. These results are compared in Figure 8.1.",
     "The CNN achieved a validation accuracy of 90% and an accuracy of 80% on new leaf images. These results are compared in Figure 8.1."),
    ("F: fig8_1_accuracy.png | Figure 8.1: Classifier accuracy on the validation set, on new leaves and in leak-free cross-validation | 5.2",
     "F: old_fig8_1_accuracy.png | Figure 8.1: Classifier accuracy on the validation set and on new leaves | 4.6"),
    ("""The leak-free evaluation was added because an audit of the JMuBEN dataset found that its 58,549 files come from only 861 distinct leaf patches, so a random split places a copy of almost every test image in the training set. With every copy of a patch kept on the same side of each fold, the classifier reaches an accuracy of 97.9%. The hardest pair is Phoma Blight and leaf miner, and the F1-score for Phoma Blight is 0.949. At the 75% confidence gate, the classifier answers 99.3% of the images, with an accuracy of 98.1% on those it answers. These images are close-up, evenly lit patches from a single dataset, so the figure is an upper bound for field photographs.
Per-class precision and recall on field photographs have not yet been calculated, so it cannot be claimed that one disease is recognised in the field more reliably than another.""",
     """Per-class precision and recall for the final model have not been calculated in this report, so it cannot be claimed that one disease is recognised more reliably than another."""),
    ("""| Operation | Time | Note |
| Script detection in the fallback router | 0.08 ms | A regular-expression check |
| CNN cache hit | 0.85 ms | Repeat request |
| CNN inference on the GPU | 5.3 ms | Median, after the GPU is initialised |
| CNN inference on the CPU | 54.9 ms | Median |
| CNN cold start | 704 ms | First call includes CUDA initialisation |
| Chat turn without the language model | 0.22 s | Median: CNN, routing, weather and retrieval |
| Hybrid retrieval | About 0.4 s | Dense, BM25, fusion and rerank |
| Complete advisory | About 6 s | Dominated by language-model generation |""",
     """| Operation | Time | Note |
| Script detection in the pre-router | 0.08 ms | A regular-expression check |
| CNN cache hit | 0.85 ms | Repeat request |
| CNN warm inference | 14.2 ms | After the GPU is initialised |
| CNN cold start | 704 ms | First call includes CUDA initialisation |
| Whole test suite | About 103 s | 48 tests |"""),
    ("F: fig8_2_latency.png | Figure 8.2: Response times of the main operations (logarithmic scale) | 5.6",
     "F: old_fig8_2_latency.png | Figure 8.2: Response times of the main operations (logarithmic scale) | 5.4"),
    ("A cache hit is about six times faster than a warm inference on the GPU (0.85 ms compared with 5.3 ms) and over 800 times faster than a cold start. All of these numbers are small compared with the language-model call and the network, which dominate the time that the grower waits for a complete advisory (about 6 s).",
     "A cache hit is 17 times faster than a warm inference (0.85 ms compared with 14.2 ms) and over 800 times faster than a cold start. All of these numbers are small compared with the language-model call and the network, which dominate the time that the grower waits for."),
    ("Several results differed from the plan, and most of these deviations were found by the automated tests or the benchmarks.",
     "Several results differed from the plan, and most of these deviations were found by the automated tests."),
    ("Later calls take a median of 5.3 ms on the GPU.", "Later calls take about 14.2 ms on the GPU."),
    (' A later benchmark showed that doses written in words, such as "four litres", were also missed; number words are now converted to digits before the check.', ""),
    ("""Gemini 2.5 Flash sometimes spent its output budget on internal "thinking" tokens and returned an advisory cut short at about 100 characters. Thinking was turned off and the output budget was raised. An empty reply, or a reply that stops at the token limit, is now treated as a failure that moves the request to Groq.""",
     """The language model occasionally returned an empty reply, which the first version of the generator accepted as an answer. A guard now treats an empty reply as a failure that moves the request to the next fallback, and a regression test checks this behaviour."""),
    ("The Groq fallback and the offline guide kept every test passing,", "The Groq and CCRI fallbacks kept every test passing,"),
    ("""=== 8.4.6 Chatbot Faults Found by the Benchmark
Three faults were exposed by the chatbot benchmark. The language router saw only the current message, so two of ten follow-up questions were answered wrongly; weather keywords matched inside two Kannada compound words; and the offline reply for Kannada users quoted English excerpts. The router now receives the last two exchanges, weather keywords must start a word, and the offline Kannada reply cites the document pages in Kannada. Regression tests were added for all three fixes.
""", ""),
    ("| Language router and English search query | Neural translation of Kannada | One short routing call (0.08 ms script check as fallback); no translation of the answer |",
     "| Regex pre-router and English search query | Neural translation of Kannada | Script check takes 0.08 ms; no separate translation call |"),
    ("| SHA-256 result cache | Re-running the CNN on every scan | 0.85 ms cache lookup against 5.3 ms inference per repeat |",
     "| SHA-256 result cache | Re-running the CNN on every scan | 0.85 ms cache lookup against 14.2 ms inference per repeat |"),
    ("""To compare the retrieval designs on equal terms, a dense-only pipeline was re-implemented and run on the same questions with the same language model; the results are given in Table 8.4. On 75 Karnataka coffee questions (21 of them in Kannada), the hybrid retriever found the gold evidence in its top three passages for 0.867 of the questions, against 0.500 for dense-only retrieval. With the same language model, the PlantIQ answers were correct for 0.944 of 54 English questions, against 0.824 for the dense pipeline and 0.611 without retrieval; without retrieval, 20.4% of the answers stated a dose that was not in any supplied document, against none for PlantIQ. On 43 test conversations, the chatbot behaved as expected in all 43, against 15 for a conversational chain built on the dense pipeline.
T: Table 8.4: Advisory and chatbot benchmark results
W: 40,20,22,18
| Measure | PlantIQ | Dense-only pipeline | No retrieval |
| Evidence in top 3 passages (75 questions) | 0.867 | 0.500 | n/a |
| Evidence in top 3 passages (21 Kannada questions) | 0.905 | 0.095 | n/a |
| Correct answers (54 English questions) | 0.944 | 0.824 | 0.611 |
| Answers with an unsupported dose | 0.0% | 0.0% | 20.4% |
| Conversations with the expected behaviour (43) | 43 | 15 | n/a |
| Correct chatbot answers (29 knowledge questions) | 0.91 | 0.38 | n/a |

The answers and their scores were produced by a single language model from the exact prompts of each system, and the questions were written from the same documents, so these figures should be confirmed with human judges and a question set collected from growers.
""", """It is not a comparison of the two systems on the same data, and it cannot be claimed that PlantIQ is more accurate than any other system.
"""),
    ("# **Synthetic test data:** The fast automated tests use synthetic and deliberately corrupted images; only the four real-model tests use real sample photographs.",
     "# **Synthetic test data:** The automated tests are based on synthetic and deliberately corrupted images."),
    ("indicating that field performance is lower than laboratory performance, and the leak-free 97.9% was measured on close-up patches from one dataset.",
     "indicating that field performance is lower than laboratory performance."),
    ("so the Groq and offline fallbacks are crucial,", "so the Groq and CCRI fallbacks are crucial,"),
    ("Soil data is not used in the current build, and severity is not assessed.", "Soil data and elevation are not used in the current build, and severity is not assessed."),
    ("# **Benchmarks written by the team:** The retrieval and chatbot questions were written from the knowledge-base documents and scored by a language model, so a question set collected from growers is still needed.\n", ""),
    ("Eight risks were listed in the Phase 2 report; their status at the end of Phase 3 is given in Table 8.5.\nT: Table 8.5: Status of the Phase 2 risks",
     "Eight risks were listed in the Phase 2 report; their status at the end of Phase 3 is given in Table 8.4.\nT: Table 8.4: Status of the Phase 2 risks"),
    ("| Mitigated: Gemini to Groq to offline guide;", "| Mitigated: Gemini to Groq to CCRI fallback;"),
    ("proximity computed with Haversine in the application; 500 listings sorted within 1.5 s; to be revisited", "proximity computed with Haversine in the application; to be revisited"),
    ("with a 75% confidence gate and a SHA-256 cache that skips repeat inference; 97.9% accuracy in leak-free cross-validation |",
     "with a 75% confidence gate and a SHA-256 cache that skips repeat inference |"),
    ("| RAG | Dense, BM25, RRF and cross-encoder retrieval with live microclimate input, a spray window and a dosage audit",
     "| RAG | Dense, BM25, RRF and cross-encoder retrieval with live microclimate input and a dosage audit"),
    ("| Chatbot | Voice and text in Kannada, Kanglish and English, with a language router, conversation memory and scan-to-chat context |",
     "| Chatbot | Voice and text in Kannada, Kanglish and English, with a lightweight pre-router and scan-to-chat context |"),
    ("| Marketplace | Direct grower-to-buyer listings with photo galleries, unit normalisation, Haversine", "| Marketplace | Direct grower-to-buyer listings with photo galleries, Haversine"),
    ("| Whole system | Integrated end to end, with 373 of 373 automated tests passing across modules, integration, security and the frontend |",
     "| Whole system | Integrated end to end, with 48 of 48 automated tests passing across modules, integration and security |"),
    ("Kannada language router and three-tier speech chain; automated test suite of 373 tests; leak-free classifier evaluation; retrieval and chatbot benchmarks; initial field feedback |",
     "Kannada pre-router and three-tier speech chain; automated test suite of 48 tests; initial field feedback |"),
    ("By detecting the language, searching in English and writing the answer in Kannada, a separate translation step was removed",
     "By detecting the script, searching in English and writing the answer in Kannada, a whole model call was removed"),
    ("A fast suite meant that it was run constantly,", "A suite that runs in under two minutes meant that it was run constantly,"),
    ("The advisory has been tested automatically and benchmarked, but it has not been re-evaluated", "The advisory has been exercised and tested, but it has not been re-evaluated"),
    ("| bge-m3 | A multilingual text-embedding model used for dense retrieval |\n", ""),
    ("If every chemical dose in the advice is found in the source text, the advisory is marked as verified; if any dose is not found, a caution is shown with the unverified quantities. Treat the caution as a reminder",
     "If a chemical dose mentioned in the advice is found in the source text, it is marked VERIFIED; if it is not found, it is marked CAUTION. Treat CAUTION as a reminder"),
]

OLD_REFS = """R: S. Selva Kumar, I. A. Banday, V. V. Shanbhag, A. K. M. A. Khan and M. Gada, "Overcoming LLM challenges using RAG-driven precision in coffee leaf disease remediation," in ~IEEE Int. Conf. Emerging Technologies in Computer Science~, 2024.
R: X. Zhao et al., "Implementation of large language models and agricultural knowledge graphs for efficient plant disease detection," ~Agriculture~, vol. 14, no. 8, 2024.
R: A. K. S. et al., "Coffee leaf disease detection using convolution neural network," ~Grenze Int. J. Eng. Technol.~, 2024.
R: R. Sapkota et al., "Multi-modal LLMs in agriculture: A comprehensive review," ~IEEE Trans. Autom. Sci. Eng.~, 2024.
R: N. Singh et al., "Farmer.Chat: Scaling AI-powered agricultural services for smallholder farmers," in ~ACM Proceedings~, 2024.
R: C. S. Santhosha and K. K. Umesh, "An ensemble approach for coffee crop yield prediction based on agronomic factors," ~ASEAN Eng. J.~, vol. 13, no. 3, 2023.
R: S. Patil et al., "Influence of elevation and rainfall on leaf growth, bean characteristics and yield components of coffee under changing climatic conditions in Karnataka, India," ~J. Plantation Crops~, vol. 50, no. 2, pp. 78-84, 2022.
"""

OLD_T72 = """| Member | Module | Test file and responsibility |
| Mohammed Ayaan | CNN | test_cnn.py (7 tests): weights, architecture, preprocessing, softmax sums to 100%, SHA-256 cache, corrupted input, 75% confidence gate |
| Jeel Nada | RAG | test_rag.py (9 tests): zero-mock weather, spore-risk logic, FAISS and BM25, RRF, sigmoid bounds, dosage audit, end-to-end advisory |
| Nidhi N | Chatbot and marketplace | test_chatbot.py (5 tests): Kannada and English routing, GPS parsing, thread and image persistence. test_market.py (4 tests): listing with photos, Haversine, WhatsApp and tel: URLs, filters |
| All three | Integration and security | test_integrated.py (7 tests) and test_security.py (8 tests), each member testing the endpoints of their own module |
"""

OLD_APPC = """= APPENDIX C | AUTOMATED TEST CATALOGUE
The 48 tests are grouped by file and area in Table C.1, which also states what each group checks.
T: Table C.1: Test groups
W: 24,10,66
| Group | Count | What it checks |
| test_cnn.py | 7 | Model weights load; architecture and five-class head; preprocessing; softmax sums to 100%; SHA-256 cache behaviour; corrupted input handled; 75% confidence gate |
| test_rag.py | 9 | Zero-mock weather; spore-risk logic; FAISS and BM25 index integrity; RRF arithmetic; sigmoid bounds; dosage audit; end-to-end advisory |
| test_chatbot.py | 5 | Kannada and English routing; GPS parsing; thread persistence; image persistence |
| test_market.py | 4 | Listing with photos; Haversine distance; WhatsApp and tel: URLs; price and keyword filters |
| test_integrated.py | 7 | Authentication; scan to CNN to RAG advisory; cache hit; scan-to-chat hand-off; marketplace to Maps and WhatsApp |
| test_security.py | 8 | Authentication and tokens; cross-user isolation (403); unauthorised access (401); SQL injection; cross-site scripting; dosage guardrail; corrupted uploads |
| Performance | 8 | Latency and concurrency checks, including 10 parallel workers; results depend on the test hardware |
| Total | 48 | All passing; the suite runs in about 103 seconds |

"""

OLD_D1 = """| Mohammed Ayaan | PES2UG23AM058 | CNN model, ResNet-50 fine-tuning, inference and cache; tests in test_cnn.py |
| Jeel Nada | PES2UG23CS357 | Hybrid RAG engine, knowledge base and indexes, LLM integration, dosage audit; tests in test_rag.py |
| Nidhi N | PES2UG23CS384 | Chatbot, speech chain and pre-router, marketplace; tests in test_chatbot.py and test_market.py |
| All three | | Integration, security testing (test_integrated.py and test_security.py), report and demonstration |
"""


def block_replace(text, start_marker, end_marker, new):
    a = text.index(start_marker)
    b = text.index(end_marker, a)
    return text[:a] + new + text[b:]


def main():
    for n in (1, 2, 3):
        s = open(f"content_{n}.txt", encoding="utf-8").read().lstrip("﻿")
        for old, new in R[n]:
            if old == new:
                continue
            c = s.count(old)
            assert c == 1, f"content_{n}: pattern found {c} times: {old[:80]!r}"
            s = s.replace(old, new)
        # figures with the original data
        s = s.replace("F: fig5_1_architecture.png", "F: old_fig5_1_architecture.png")
        s = s.replace("F: fig6_1_rag_pipeline.png", "F: old_fig6_1_rag_pipeline.png")
        s = s.replace("F: fig6_2_speech_chain.png", "F: old_fig6_2_speech_chain.png")
        if n == 2:
            s = block_replace(s, "| Method | Tests | Why it is needed |", "\nThe integration tests exercise", OLD_T63)
        if n == 3:
            s = block_replace(s, "R: S. Selva Kumar", "\n= APPENDIX A", OLD_REFS)
            s = block_replace(s, "| Member | Module | Tests and responsibility |", "\nThe testing tools used", OLD_T72)
            s = block_replace(s, "= APPENDIX C |", "= APPENDIX D |", OLD_APPC)
            s = block_replace(s, "| Mohammed Ayaan | PES2UG23AM058 |", "\x00", OLD_D1) if "\x00" in s else \
                s[:s.index("| Mohammed Ayaan | PES2UG23AM058 |")] + OLD_D1
            s = s.replace("T: Table 7.2: Individual contribution towards testing\nW: 18,22,60",
                          "T: Table 7.2: Individual contribution towards testing\nW: 18,20,62")
        open(f"content_old_{n}.txt", "w", encoding="utf-8").write(s)
        print(f"content_old_{n}.txt written")


if __name__ == "__main__":
    main()
