# 🌿 PlantIQ — Cleaned & Production-Ready Edition (v2.0)

This directory contains the **modularized, production-ready version** of the **PlantIQ** platform. It features a modern multi-page semantic frontend, decoupled FastAPI backend services, a **native Android APK build system (Capacitor 7)**, an **in-app dynamic Server IP switcher**, and full multimodal leaf diagnostics with microclimate intelligence.

---

## 🏗️ Project Architecture

```
d:\end-capstone-project\cleaned\
├── backend\                           # FastAPI Monolithic Service Layer
│   ├── app\
│   │   ├── main.py                    # App factory, static mounting & page routing
│   │   ├── core\
│   │   │   ├── config.py              # Environment configuration & settings
│   │   │   ├── database.py            # SQLite database engine & sessionmaker
│   │   │   └── security.py            # PBKDF2 hashing, bearer tokens & auth guards
│   │   ├── models\                   # Declarative ORM Database Models
│   │   │   ├── user.py                # Farmer user model
│   │   │   ├── cache.py               # ImageAnalysisCache (SHA-256 deduplication)
│   │   │   ├── chat.py                # ChatThread & ChatMessage (with persistent photos)
│   │   │   └── marketplace.py         # CropListing model (multi-photo & JSON captions)
│   │   ├── schemas\                  # Pydantic Request/Response Models
│   │   │   ├── auth.py
│   │   │   ├── predict.py
│   │   │   ├── chat.py
│   │   │   ├── voice.py
│   │   │   └── marketplace.py
│   │   ├── api\                      # Modular REST API Routers
│   │   │   ├── router.py              # Central API router aggregator (/api)
│   │   │   ├── auth.py                # /api/auth (register, login, me)
│   │   │   ├── predict.py             # /api/predict (ResNet50 + RAG advisory)
│   │   │   ├── chat.py                # /api/chat (threads, multimodal messages)
│   │   │   ├── voice.py               # /api/voice/transcribe (STT)
│   │   │   ├── marketplace.py         # /api/marketplace (listings, multi-photo, filter)
│   │   │   └── environment.py         # /api/environment/live (Open-Meteo)
│   │   └── services\                 # Decoupled AI & Business Logic
│   │       ├── cnn_service.py         # PyTorch ResNet50 Classifier (20ms local inference)
│   │       ├── cache_service.py       # SHA-256 composite deduplication hashing
│   │       ├── rag_service.py         # 3-Stage Hybrid RAG (BGE-Base + BM25 + Cross-Encoder Reranker)
│   │       ├── build_index.py         # Semantic Section Chunker & Multi-Threaded Ingestion Engine
│   │       ├── router_service.py      # Linguistic Pre-Router (Kannada/Kanglish/English)
│   │       ├── chat_service.py        # Multi-turn context & past scan metadata ingestion
│   │       ├── voice_service.py       # Gemini 1.5 Audio & Groq Whisper STT
│   │       └── env_service.py         # Open-Meteo real-time microclimate provider
│   ├── requirements.txt               # Python dependencies
│   ├── .env                           # Active Environment File
│   ├── .env.example                   # Template configuration
│   └── run.py                         # Production server launcher (0.0.0.0:8000)
├── frontend\                          # Multi-Page Semantic Web Interface
│   ├── static\
│   │   ├── css\
│   │   │   ├── base.css               # Design system tokens, dark mode, modal overlays
│   │   │   ├── navbar.css             # Header with live server status & bottom tab bar
│   │   │   ├── scanner.css            # Upload dropzone & diagnosis meters
│   │   │   ├── chat.css               # Multimodal message bubbles & attachment preview
│   │   │   ├── marketplace.css        # Listing cards, dual price sliders & photo galleries
│   │   │   ├── profile.css            # Farmer account dashboard & stats
│   │   │   └── auth.css               # Sign In & Registration forms
│   │   └── js\
│   │       ├── api.js                 # Dynamic Server IP switcher, auth guard & markdown
│   │       ├── i18n.js                # Bilingual dictionary & reactive language switcher
│   │       ├── location.js            # Auto GPS vs Manual entry & Google Maps guide
│   │       ├── voice.js               # MediaRecorder capture & language modal prompt
│   │       ├── scanner.js             # Leaf diagnosis, distribution & scan-to-chat handoff
│   │       ├── chat.js                # Multimodal image picker & persistent chat memory
│   │       ├── marketplace.js         # Listings tabs, multi-photo uploader & WhatsApp
│   │       ├── profile.js             # History report modal & 3s Undo toast
│   │       └── auth.js                # Form submission & token storage
│   └── templates\                     # Dedicated Semantic HTML Pages
│       ├── index.html                 # Leaf Disease Diagnostic (Home)
│       ├── chat.html                  # Agri Chatbot Assistant
│       ├── marketplace.html           # Coffee Crop Marketplace
│       ├── history.html               # Diagnostic History Feed
│       ├── profile.html               # Farmer Account & Stats
│       └── auth.html                  # Sign In & Registration
└── mobile\                            # Native Android Project (Capacitor 7)
    ├── package.json                   # Capacitor dependencies
    ├── capacitor.config.json          # App ID, cleartext traffic & webDir config
    ├── www\                           # Static export bundle
    └── android\                       # Native Android Studio Project ready for APK build
```

---

## 🚀 Running the Web Backend

### 1. Configure Environment Variables
Create or verify `.env` in `cleaned/backend/`:
```env
PORT=8000
HOST=0.0.0.0
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key_here
```

### 2. Install Dependencies
```bash
cd cleaned/backend
pip install -r requirements.txt
```

### 3. Launch Backend Server
```bash
python run.py
```
Access the web app at **`http://127.0.0.1:8000`** in your browser!

---

## 📱 Mobile APK Build & Testing Guide

PlantIQ includes a complete **Capacitor 7 Android project** in `cleaned/mobile/` that compiles directly into an installable `.apk` file for real mobile phones.

### ⚙️ How the App Connects to Your Laptop (In-App Dynamic IP Switcher)
When the APK is installed on your phone, you do **not** need to hardcode IP addresses or recompile when switching Wi-Fi networks:

1. Look at the **top navigation bar** in the app — there is a **Server icon** (`<i data-lucide="server"></i>`) with a live status dot:
   * 🟢 **Green**: Connected to backend server.
   * 🔴 **Red**: Server disconnected / unreachable.
2. Tap the **Server icon** to open the **Backend Server Connection Modal**.
3. Enter your laptop's current Wi-Fi IP address (from running `ipconfig` in your laptop's terminal) with port `8000`:
   ```
   192.168.1.15:8000
   ```
   *(Or enter a cloud URL like `https://plantiq.onrender.com` if hosted online)*.
4. Tap **"Test Ping"**: The app measures network latency in real-time.
5. Tap **"Save & Connect"**: The app saves the IP in phone storage and connects immediately.

---

### 🔨 Building the Android APK File

#### Step 1: Open Terminal in Mobile Directory
```bash
cd d:\end-capstone-project\cleaned\mobile
```

#### Step 2: Open in Android Studio
```bash
npx.cmd cap open android
```

#### Step 3: Build or Rebuild APK (1-Click)
Whenever you make any changes to your code, you can rebuild the APK in **10 seconds** by running:
```bash
cd d:\end-capstone-project\cleaned\mobile
python build_apk.py
```
*(Or double-click `build_apk.bat`)*.

It automatically syncs all frontend files, updates Capacitor, recompiles Gradle, and puts the fresh **`PlantIQ.apk`** right in `cleaned/mobile/PlantIQ.apk`!

#### Step 4: Testing with Friends Remotely (3 Methods)

##### Method A: Cloudflare Tunnel (Zero Password, 100% Free — Recommended)
To let friends test from their phones anywhere with zero verification screens:
1. Keep the backend running in Terminal 1:
   ```bash
   cd d:\end-capstone-project\cleaned\backend
   python run.py
   ```
2. Open a **new terminal window** and run:
   ```bash
   npx.cmd cloudflared tunnel --url http://127.0.0.1:8000
   ```
3. It prints a free direct HTTPS URL (e.g. `https://random-words.trycloudflare.com`).
4. Share `PlantIQ.apk` with your friends on WhatsApp along with that link.
5. In the app on their phone, they tap the **Server icon** $\rightarrow$ enter `https://random-words.trycloudflare.com` $\rightarrow$ tap **Save & Connect**!

##### Method B: Localtunnel
```bash
npx.cmd localtunnel --port 8000
```
*Note: PlantIQ APK automatically passes the `Bypass-Tunnel-Reminder` header to bypass the HTTP 511 interstitial screen.*

##### Method C: 24/7 Free Cloud Hosting on Render.com
For permanent 24/7 testing without needing your laptop turned on:
1. Push `cleaned/backend` to GitHub.
2. Create a free **Web Service** on [Render.com](https://render.com).
3. Set **Build Command**: `pip install -r requirements.txt` and **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Add environment variables (`GEMINI_API_KEY`, `GROQ_API_KEY`, `SECRET_KEY`).
5. Render generates a permanent URL (e.g. `https://plantiq-api.onrender.com`) for all your evaluators and friends to use 24/7!

---

## 🌟 Key Application Features

### 1. 🔬 Leaf Diagnostic Scanner
* **PyTorch ResNet50 Classifier**: Identifies *Coffee Leaf Rust*, *Cercospora Leaf Spot*, *Phoma*, *Leaf Miner*, and *Healthy Leaf*.
* **Open-Meteo Microclimate Engine**: Detects site elevation, temperature, humidity, rainfall, wind speed, and soil pH.
* **CCRI Agronomic Advisory**: Provides verified chemical fungicide dosages (Bordeaux mixture 1%, Bayleton, Contaf, Tilt) and organic cultural shade practices.

### 2. 💬 Multimodal Agri Chatbot
* **Image Context Attachment**: Upload fresh photos from the phone camera or pick past scans from device history.
* **Scan Metadata Ingestion**: Ingests historical microclimate weather conditions and previous scan treatment advisories directly into LLM reasoning.
* **Multi-Turn Persistent Chat**: Saves chat history and attached photos across page navigation and app restarts.
* **Voice Speech-to-Text**: Bilingual voice microphone input in English and native Kannada (`ಕನ್ನಡ`).

### 3. 🛒 Coffee Crop Marketplace
* **Tabbed View**: Filter between **All Listings** and **Your Listings**.
* **Inline Estate GPS**: Capture plot coordinates automatically or enter latitude/longitude with a bilingual Google Maps guide.
* **Multi-Photo Galleries**: Upload multiple crop photos (drying yard, parchment, lot) with individual per-photo description captions.
* **1-Tap Contact**: Direct phone calls, WhatsApp messaging, and Google Maps estate navigation links.

### 4. 📜 Diagnostic History
* **Complete Diagnostic Report Modal**: View high-res photo, confidence ratings, class probabilities, weather factors, and CCRI advisories.
* **3-Second Animated Undo Toast**: Safely delete single scans or clear history with a 3-second instant restoration timer.

---

## 🏛️ Comprehensive Technical Architecture & Defense Documentation

For academic defense, capstone evaluations, and in-depth engineering documentation, refer to the module specifications in [`docs/architecture/`](file:///d:/end-capstone-project/cleaned/docs/architecture/):

1. 🏛️ [**`00_SYSTEM_ARCHITECTURE_OVERVIEW.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/00_SYSTEM_ARCHITECTURE_OVERVIEW.md) — System Topology & Data Flow
2. 🔬 [**`01_CNN_DIAGNOSTICS_MODULE.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/01_CNN_DIAGNOSTICS_MODULE.md) — ResNet-50 Deep Residual Learning & Loss Functions
3. 📚 [**`02_ADVANCED_HYBRID_RAG_MODULE.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/02_ADVANCED_HYBRID_RAG_MODULE.md) — BGE-Base Dense + BM25 Lexical + Cross-Encoder Reranker
4. 💬 [**`03_MULTIMODAL_CHATBOT_AND_ROUTING.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/03_MULTIMODAL_CHATBOT_AND_ROUTING.md) — Kanglish/Kannada Linguistic Router & LLM Failover
5. ⛅ [**`04_MICROCLIMATE_RISK_ENGINE.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/04_MICROCLIMATE_RISK_ENGINE.md) — Open-Meteo NWP Reanalysis & Disease Risk Indices
6. 🛒 [**`05_MARKETPLACE_AND_SPATIAL_DISCOVERY.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/05_MARKETPLACE_AND_SPATIAL_DISCOVERY.md) — Spatial Haversine Routing & Intent Dispatch
7. 📱 [**`06_MOBILE_EDGE_AND_SYSTEM_SECURITY.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/06_MOBILE_EDGE_AND_SYSTEM_SECURITY.md) — Capacitor 7 Native Container & PBKDF2/JWT Cryptography
8. 🎓 [**`07_PROFESSOR_DEFENSE_AND_CROSS_EXAMINATION_GUIDE.md`**](file:///d:/end-capstone-project/cleaned/docs/architecture/07_PROFESSOR_DEFENSE_AND_CROSS_EXAMINATION_GUIDE.md) — Strict Technical Defense Q&A, Mathematical Proofs & Architectural Tradeoffs
