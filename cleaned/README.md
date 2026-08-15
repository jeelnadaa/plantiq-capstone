# 🌿 PlantIQ — Cleaned & Production-Ready Standalone Edition (v2.0)

This directory contains the **modularized, refactored, production-ready version** of the **PlantIQ** platform. It maintains 100% feature parity with the original monolithic architecture while introducing a clean multi-page frontend, decoupled backend services, an elevated UI aesthetic for A/B testing, and self-contained environment configs.

---

## 🏗️ Modular Folder Structure

```
d:\end-capstone-project\cleaned\
├── backend\                           # FastAPI Monolithic Service Layer
│   ├── app\
│   │   ├── main.py                    # App factory, static mounting & page routing
│   │   ├── core\
│   │   │   ├── config.py              # Pydantic v2 BaseSettings
│   │   │   ├── database.py            # SQLAlchemy engine & sessionmaker
│   │   │   └── security.py            # JWT token creation, password hashing & dependencies
│   │   ├── models\                   # Declarative ORM Database Models
│   │   │   ├── user.py                # User account model
│   │   │   ├── cache.py               # ImageAnalysisCache model (SHA-256 deduplication)
│   │   │   ├── chat.py                # ChatThread & ChatMessage models
│   │   │   └── marketplace.py         # CropListing model
│   │   ├── schemas\                  # Pydantic Request/Response Models
│   │   │   ├── auth.py
│   │   │   ├── predict.py
│   │   │   ├── chat.py
│   │   │   ├── voice.py
│   │   │   └── marketplace.py
│   │   ├── api\                      # Modular REST API Routers
│   │   │   ├── router.py              # Central API Router aggregator (/api)
│   │   │   ├── auth.py                # /api/auth (register, login, me)
│   │   │   ├── predict.py             # /api/predict (CNN + RAG advisory)
│   │   │   ├── chat.py                # /api/chat (threads, messages, handoff)
│   │   │   ├── voice.py               # /api/voice/transcribe (STT)
│   │   │   ├── marketplace.py         # /api/marketplace (listings, filter, delete)
│   │   │   └── environment.py         # /api/environment/live
│   │   └── services\                 # Decoupled AI & Business Logic
│   │       ├── cnn_service.py         # PyTorch ResNet50 Classifier
│   │       ├── cache_service.py       # SHA-256 composite hashing
│   │       ├── rag_service.py         # FAISS vector search & Gemini/Groq blending
│   │       ├── router_service.py      # Multilingual Pre-Router (Kannada/Kanglish/English)
│   │       ├── chat_service.py        # Multi-turn sequential context management
│   │       ├── voice_service.py       # Gemini 1.5 Audio & Groq Whisper STT
│   │       └── env_service.py         # Open-Meteo real-time microclimate provider
│   ├── requirements.txt               # Dependencies
│   ├── .env                           # Active Environment File
│   ├── .env.example                   # Template configuration
│   └── run.py                         # Production server launcher
├── frontend\                          # Multi-Page Semantic Web Interface
│   ├── static\
│   │   ├── css\
│   │   │   ├── base.css               # Design system tokens (glassmorphic, emerald palette)
│   │   │   ├── navbar.css             # Sticky header & bottom tab bar
│   │   │   ├── scanner.css            # Dropzone & diagnosis meters
│   │   │   ├── chat.css               # Message bubbles & typing indicators
│   │   │   ├── marketplace.css        # Listing cards & dual price range sliders
│   │   │   ├── profile.css            # Stats cards & account views
│   │   │   └── auth.css               # Login & registration forms
│   │   └── js\
│   │       ├── api.js                 # Centralized fetch client & JWT header interceptor
│   │       ├── i18n.js                # Bilingual dictionary & reactive language switcher
│   │       ├── location.js            # Auto GPS vs Manual entry & Google Maps guide
│   │       ├── voice.js               # MediaRecorder capture & language modal prompt
│   │       ├── scanner.js             # Leaf diagnosis, distribution & scan-to-chat handoff
│   │       ├── chat.js                # Multi-turn conversational memory & markdown parsing
│   │       ├── marketplace.js         # Listings feed, price sliders, WhatsApp & deletion
│   │       ├── profile.js             # User account dashboard & statistics
│   │       └── auth.js                # Form submission & token storage
│   └── templates\                     # Dedicated Semantic HTML Pages
│       ├── index.html                 # Leaf Disease Diagnostic (Home)
│       ├── chat.html                  # Agri Chatbot Assistant
│       ├── marketplace.html           # Coffee Crop Marketplace
│       ├── history.html               # Diagnostic History Feed
│       ├── profile.html               # Farmer Account & Stats
│       └── auth.html                  # Sign In & Registration
└── README.md
```

---

## 🚀 Quickstart & How to Run

### 1. Configure Environment
Verify `.env` in `cleaned/backend/`:
```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

### 2. Install Dependencies
```bash
cd cleaned/backend
pip install -r requirements.txt
```

### 3. Launch Server
```bash
python run.py
```
Open your browser at `http://127.0.0.1:8000` to access the refreshed multi-page PlantIQ application!
