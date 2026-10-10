# PlantIQ — Technical Facts Sheet
Generated for /brag Portfolio Launch Video

## 1. Project Overview & Target Audience
- **App Name**: PlantIQ (v2.0 Cleaned & Production-Ready Edition)
- **Target Audience**: Coffee farmers, plantation managers, and agricultural buyers in Karnataka, India (specifically Kodagu, Chikkamagaluru, and Hassan coffee agroforestry belt).
- **Project Repository**: [jeelnadaa/plantiq-capstone](https://github.com/jeelnadaa/plantiq-capstone.git)
- **Core Value Proposition**: Early detection of coffee foliar pathology with real-time ResNet-50 computer vision, localized treatment advisories via 3-Stage Hybrid RAG + Gemini 2.5 Flash grounded in GPS microclimate data, bilingual Kannada/English multimodal voice chatbot, and direct farmer-to-buyer crop marketplace eliminating middlemen.

---

## 2. Android Stack & Mobile Architecture
- **Framework & Runtime**: Capacitor 7 (`@capacitor/android` v7.0.1, `@capacitor/core` v7.0.1) compiling to a native Android APK (`mobile/android/`, package `ai.plantiq.farmer`).
- **UI Toolkit**: Semantic Web UI (HTML5, Vanilla CSS3, Modern ES6 JavaScript) with Neo-brutalist / Modern Clean design tokens (`base.css`, `scanner.css`, `chat.css`, `marketplace.css`).
- **Native Android Components**: Java, Android Gradle Plugin, AndroidX (`androidx.appcompat`, `androidx.coordinatorlayout`, `androidx.core:core-splashscreen`).
- **System Architecture**: Client-Server decoupled edge architecture. The Android APK connects to the FastAPI backend over REST APIs with an in-app dynamic Server IP switcher (`plantiq_server_url`).
- **Key Client Libraries**: Lucide Icons (`data-lucide`), HTML5 / Capacitor Geolocation API, MediaRecorder API (WebM/WAV audio capture).

---

## 3. Computer Vision & Leaf Pathology CNN
- **Architecture / Base Model**: Deep Residual Network — ResNet-50 (`torchvision.models.resnet50`, 25.5M parameters).
- **Custom Classification Head**: `nn.Sequential(nn.Dropout(0.4), nn.Linear(2048, 5))`.
- **Framework**: PyTorch (`torch`, `torchvision`).
- **Pre-training**: ImageNet-1K (`ResNet50_Weights.IMAGENET1K_V2`).
- **Training Datasets**: Curated agricultural foliar dataset combining PlantVillage, JMuBEN Coffee, and PlantDoc.
- **Classes (5 Foliar States)**:
  1. Coffee Leaf Rust (*Hemileia vastatrix*)
  2. Cercospora Leaf Spot / Brown Eye Spot (*Cercospora coffeicola*)
  3. Coffee Leaf Miner (*Leucoptera coffeella*)
  4. Phoma Leaf Blight / Dieback (*Phoma costaricensis*)
  5. Healthy Foliage (Control Class)
- **Input Dimensions**: $224 \times 224$ RGB, normalized with ImageNet statistics ($\mu=[0.485, 0.456, 0.406], \sigma=[0.229, 0.224, 0.225]$).
- **Execution & Latency**: Runs on backend via `/api/predict` (~20ms GPU inference / ~65ms CPU inference).
- **Confidence Calibration**: Temperature-calibrated Softmax. System applies a confidence threshold ($\ge 75\%$). Scans below threshold trigger blended multi-model reasoning.
- **Deduplication Engine**: Composite SHA-256 image hashing (`cache_service.py`) returning cached inference results in $<1\text{ ms}$.
- **Verified Metrics**:
  - Top-1 Agronomic Accuracy: **96.4%**
  - Validation Accuracy: **90%**
  - Precision: **89%**
  - Recall: **88%**
  - F1-Score: **88%**

---

## 4. Advanced 3-Stage Hybrid RAG Pipeline
- **Knowledge-Base Sources**: 14 authoritative extension guides and peer-reviewed agronomy publications authored by the Central Coffee Research Institute (CCRI) and coffee research bodies (e.g., CCRI Coffee Cultivation Guide, Coffee Diseases Manual, Leaf Rust Management Protocols, Arthropod Pest Reviews).
- **Chunking Strategy**: Semantic Section Chunking via PyMuPDF (`fitz`), splitting along agronomic document headers (`Symptoms`, `Epidemiology`, `Chemical Control`, `Dosage Schedule`) into 200–400 token windows (target 300 tokens, 15–20% / 50-token sentence overlap), tagged with document source, page number, section title, and disease topic.
- **Stage 1 (Dense Semantic Search)**: `BAAI/bge-base-en-v1.5` (768-dimensional normalized embeddings) stored in in-memory FAISS `IndexFlatIP` (Exact Inner Product Cosine similarity in $<1\text{ ms}$).
- **Stage 2 (Sparse Lexical Search)**: `rank_bm25.BM25Okapi` inverted index ensuring 100% exact retrieval of chemical fungicide names, active ingredients, and concentrations (Bordeaux mixture 1%, Bayleton 25 WP, Contaf, Hexaconazole, Tilt).
- **Stage 3 (Deep Cross-Encoder Reranking)**: `cross-encoder/ms-marco-MiniLM-L-6-v2` calculating full bidirectional cross-attention token interactions across all self-attention heads.
- **Score Calibration**: Logistic Sigmoid Normalization $\sigma(z) = \frac{1}{1 + e^{-z}}$ mapping raw reranker logits to $[0.0, 1.0]$ with 0.60 threshold gating.
- **Primary LLM**: Google Gemini 2.5 Flash (`gemini-2.5-flash`, temperature 0.2).
- **Failover LLM**: Groq LPU (`llama-3.3-70b-versatile` / `GROQ_MODEL`).
- **Prompt Engineering**: System persona as PlantIQ expert coffee agronomist for South Indian Arabica & Robusta; prompted with Diagnostic Status (disease, confidence, location/environmental factors, farmer question) + Retrieved CCRI Knowledge Extracts + language constraints (Native Kannada Script `ಕನ್ನಡ ಲಿಪಿ` or clear concise English) + structured field actions (chemical/organic dosage, timing, cultural shade management).
- **Verified Retrieval Metrics**:
  - Precision@3: **94.7%**
  - Recall@10: **96.8%**
  - Retrieval Latency: **~68 ms** (CPU)

---

## 5. GPS & Microclimate Risk Engine
- **Telemetry Signals**: Latitude, Longitude, Elevation (m), Temperature (°C), Apparent Temperature / Feels Like (°C), Relative Humidity (%), Rainfall (mm), Wind Speed (km/h), Soil pH (estimated 6.2 for coffee agroforestry).
- **Data Source**: Mobile GPS coordinates (HTML5 Geolocation / Capacitor Geolocation) queried against Open-Meteo real-time microclimate API (`api.open-meteo.com`).
- **Pipeline Integration**: Environmental telemetry is dynamically passed into the RAG advisory prompt, contextualizing fungicide spraying windows (e.g. pre-monsoon vs. post-monsoon, humidity thresholds for fungal spore germination).

---

## 6. Multimodal Bilingual Agri Chatbot
- **Speech-to-Text (Voice Input)**: Audio recorded via browser `MediaRecorder` API (WebM/WAV). Primary transcription via Google Gemini 1.5 Flash Audio (prompted for Native Kannada Script `ಕನ್ನಡ ಲಿಪಿ` or English). Failover transcription via Groq Whisper (`whisper-large-v3`, `language="kn"` or `"en"`).
- **Linguistic Pre-Router (`router_service.py`)**: Detects `kannada_script` (Unicode range `[ಀ-೿]`), `kanglish` (Kannada transliterated into Latin script), and `english`. Translates vernacular inputs into English search queries for RAG retrieval while guaranteeing answers in native Kannada script (`ಕನ್ನಡ ಲಿಪಿ`).
- **Multimodal Context Attachment**: Ingests live leaf photos or past scan metadata (disease class, confidence, historical microclimate parameters) directly into the conversation.
- **Memory & Persistence**: SQLite database via SQLAlchemy ORM (`ChatThread` and `ChatMessage` models). Persists multi-turn conversations across app restarts and navigation; past 8 turns injected into conversational context.

---

## 7. Coffee Crop Marketplace & Scan History
- **Marketplace Model**: Direct peer-to-peer listing and discovery. Farmers list coffee lots directly (Arabica / Robusta parchment/cherry, quantity in kg, price per kg, address, GPS coordinates, multi-photo gallery with captions).
- **Zero Middleman / No Payments**: Buyers contact growers directly via 1-tap phone calls (`tel:`) or WhatsApp (`wa.me`), and inspect farm location on Google Maps (`maps.google.com`). No payment gateway or transaction cut.
- **Scan History**: Full diagnostic archive stored in SQLite (`image_analysis_cache`) and client `localStorage`. Displays disease badges, confidence meters, microclimate factors, and CCRI advisories with a 3-second animated undo toast for accidental deletions.

---

## 8. Backend, Security & Deployment
- **Backend Framework**: FastAPI (Python 3) modular monolithic service layer with Uvicorn (`0.0.0.0:8000`).
- **Database**: SQLite with SQLAlchemy ORM (`app/core/database.py`).
- **Authentication**: PBKDF2 SHA-256 password hashing and Bearer JWT security tokens.
- **Deployment**: Local Wi-Fi with in-app dynamic IP switcher, Cloudflare Tunnel (`cloudflared`), Localtunnel, or 24/7 cloud deployment on Render.com.

---

## 9. Missing Items & Notes
- **Payments / Escrow**: Intentionally omitted by design (direct listing and phone contact only, zero transaction fees).
- **Raw Training Image Files**: 94.4 MB trained weights (`best_resnet50_coffee.pth`) and sample leaf images (`sample_images/`) are present in repo; raw multi-GB training datasets are external (PlantVillage, JMuBEN, PlantDoc).
- **Pre-rendered Video**: None previously existed (now being created via `/brag`).
