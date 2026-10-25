# 5. Panel guide — likely questions and short answers

## Overview
**Q: What problem does PlantIQ solve?** Late diagnosis of coffee leaf diseases, advice that ignores today's weather and is
not in Kannada, and weak market access for small growers. One app: scan → grounded advice with weather → chat → sell.

**Q: What are the four modules?** (1) ResNet-50 CNN diagnosis, (2) RAG advisory with live environmental data,
(3) multilingual multimodal chatbot with voice, (4) market discovery with unit normalisation and distance search.

**Q: Why a server instead of running everything on the phone?** bge-m3, the reranker, IndicConformer and the LLM need GBs of
memory/GPU. The phone stays light (4.6 MB APK); models can be improved without reinstalling. The server can be a laptop on the
farm Wi-Fi, so it works without internet except for the LLM and weather calls, and even those have fallbacks.

## Module 1 — CNN
**Q: Why ResNet-50?** Residual connections allow a deep network to learn fine textures (rust pustules vs Cercospora rings) without
vanishing gradients; with transfer learning it reached 96.4 % top-1, beating MobileNetV3 (89.1 %), VGG-16 (93.8 %),
ViT-B/16 (92.5 %) and DenseNet-121 (94.2 %) at ~65 ms on CPU (5 ms on our GPU).

**Q: How do you handle a photo that is not one of the five classes?** The softmax always picks a class, so we gate on confidence:
below 75 % the result is marked "not fully sure", the advice mentions look-alikes and asks to check more leaves. An explicit
"unknown" class is future work.

**Q: Why 224 × 224 and ImageNet normalisation?** It is the input the network was pre-trained and fine-tuned with; using anything
else would shift the feature distribution.

**Q: How is the image protected?** File-signature check, size/pixel limits, decompression-bomb guard, EXIF/GPS stripped and
re-encoded before the model or storage ever sees it.

## Module 2 — RAG + environment
**Q: Why RAG instead of asking the LLM directly?** LLMs hallucinate doses. RAG forces the answer to come from CCRI passages,
gives citations, and lets us automatically check every dose against the sources.

**Q: Why hybrid retrieval?** Dense embeddings capture meaning ("orange powder" ≈ "urediniospores"); BM25 catches exact
terms ("0.5 %", "Bordeaux", "200 L"). Reciprocal Rank Fusion merges the two rankings without score calibration
(RRF = Σ 1/(60 + rank)).

**Q: Why a cross-encoder reranker?** Bi-encoders compare pre-computed vectors; a cross-encoder reads the question and passage
together and is far more precise, but slower — so it only re-scores the top ~20 candidates.

**Q: What did you change compared with the first version's RAG?** Multilingual bge-m3 + bge-reranker-v2-m3 (Kannada queries work
natively), table-aware chunking, disease topic filter with relaxation, MMR to remove near-duplicate passages, reranking with a
natural-language question (top match for Cercospora rose from 0.35 to 0.94), pickle-free index, safetensors models, and an
automatic fallback to the original models on CPU.

**Q: Why FAISS flat (exact) search?** 931 vectors search in < 1 ms; approximate indexes (HNSW/IVF) trade recall for speed and only
matter at millions of vectors.

**Q: How is weather used?** Open-Meteo gives temperature, humidity, rain, wind, elevation and a 3-day forecast. A rule-based
fungal model (humidity ≥ 80 % and 20–28 °C → high risk) and a spray-window rule (first day with < 40 % rain chance and < 2 mm)
go into both the UI and the LLM prompt. If data is missing the system says so — it never invents numbers.

**Q: What if Gemini fails?** Groq answers; if both fail, a built-in bilingual disease guide plus retrieved excerpts is shown.
We also found and fixed Gemini 2.5's hidden "thinking" tokens truncating answers.

## Module 3 — Chatbot
**Q: How does it understand Kanglish?** An LLM router classifies script and produces English search keywords; a heuristic
fallback uses the Kannada Unicode range and a Kanglish word list.

**Q: How does chat use images?** An attached photo goes through the CNN and the diagnosis is placed in the prompt; a past scan
brings its disease, advice and logged weather. The prompt forbids "I cannot see images" when a diagnosis exists.

**Q: Voice for Kannada?** ai4bharat IndicConformer-600M locally on the GPU; Whisper fine-tuned on Indian-accent English; Groq
Whisper large-v3 and Gemini audio as fallbacks. The farmer chooses the language first and reviews the text before sending.

**Q: Prompt injection?** User text is cleaned and fenced inside `<user_query>`; the system instruction says to treat it as data;
output is scanned to redact keys. Tested with injection strings.

## Module 4 — Market
**Q: Why normalise units?** Farmers sell in bags, quintals or tonnes; buyers compare ₹/kg. The server converts every listing
(e.g. ₹9,500 per 50 kg bag → ₹190/kg) and filters/sorts on the normalised values.

**Q: How is "nearest" computed?** Haversine great-circle distance from the buyer's GPS to each lot's GPS.

**Q: How do you prevent abuse?** Sign-in required to sell, owner-only edit/delete, 10-digit phone validation, 50-listing quota,
report once per user, rate limits, sanitised photos.

## Security & testing
**Q: What security measures did you take?** Argon2id, short JWTs with rotating hashed refresh tokens and theft detection, lockout,
rate limits, CSP and security headers, upload sanitising, owner checks, prompt-injection fencing, secret redaction, no pickle,
patched PyTorch CVE. See [SECURITY.md](../SECURITY.md).

**Q: How did you test it?** 290 backend tests (unit, integration, functional, security, non-functional, real-model), 52 frontend
unit/component tests and 12 end-to-end tests on a Pixel-7-sized browser, all passing. See [TESTING.md](../TESTING.md).

**Q: What are the limitations?** Five classes only; knowledge base thin on Phoma/leaf-miner timing; soil pH estimated; no
payments or moderator dashboard; APK verified statically but not on a physical device in this environment.

**Q: What would you do next?** Unknown-class detection and Grad-CAM, more Kannada documents with OCR, retrieval evaluation with a
labelled question set, text-to-speech answers, moderation dashboard, price trends.
