# Packaging and Deployment Diagram
## Section 3.6 of Low Level Design Document

[MODULE: Packaging & Deployment | SECTION: 3.6 Packaging and Deployment Diagram | TYPE: Mermaid]
Source: backend/run.py, mobile/capacitor.config.json, docs/architecture/00_SYSTEM_ARCHITECTURE_OVERVIEW.md, docs/architecture/06_MOBILE_EDGE_AND_SYSTEM_SECURITY.md

```mermaid
flowchart TB
    %% ────────────────────────────────────────────────────────────────
    %% CLIENT TIER
    %% ────────────────────────────────────────────────────────────────
    subgraph ClientTier ["Client Tier (Mobile Edge & Web Browser)"]
        direction TB
        subgraph MobileApp ["Android APK (Capacitor 7 Runtime)"]
            APK_Main["MainActivity.java\n(Android OS Host)"]
            APK_Config["capacitor.config.json\n(Cleartext HTTP Allowed)"]
            APK_Sec["network_security_config.xml\n(Local Subnet Trust)"]
            APK_Web["Local Assets (/public)\nHTML5 / CSS3 / ES6"]
        end

        subgraph DesktopBrowser ["Client Browser (Desktop / Mobile PWA)"]
            UI_Pages["Web Templates\n(index, chat, marketplace)"]
            UI_JS["ES6 Scripts\n(scanner.js, chat.js, api.js)"]
            UI_Storage["HTML5 localStorage\n(JWT Token, Dynamic Server IP)"]
        end
    end

    %% ────────────────────────────────────────────────────────────────
    %% APPLICATION GATEWAY & WEB SERVER
    %% ────────────────────────────────────────────────────────────────
    subgraph GatewayTier ["Application Gateway & Host (FastAPI / Uvicorn)"]
        direction TB
        RunPy["run.py\n(Launcher: 0.0.0.0:8000)"]
        FastAPI_App["main.py\n(FastAPI Application Factory)"]
        CORS["CORSMiddleware\n(Origins: * / localhost)"]
        Security["security.py\n(PBKDF2 Hashing & JWT HS256)"]
        StaticServer["StaticFiles Mount\n(/static -> CSS / JS / Assets)"]
        APIRouter["api/router.py\n(Route Aggregator: /api)"]
    end

    %% ────────────────────────────────────────────────────────────────
    %% INTELLIGENT AI SERVICES LAYER
    %% ────────────────────────────────────────────────────────────────
    subgraph AIServiceTier ["Intelligent AI Inference Tier (Python 3.11 Runtime)"]
        direction TB
        CNN_Engine["cnn_service.py\n(ResNet-50 PyTorch Inference)"]
        Cache_Engine["cache_service.py\n(SHA-256 Deduplication Cache)"]
        RAG_Engine["rag_service.py\n(3-Stage Hybrid RAG Engine)"]
        Router_Engine["router_service.py\n(Linguistic Script Pre-Router)"]
        Chat_Engine["chat_service.py\n(Multimodal Context Fusion)"]
        Voice_Engine["voice_service.py\n(Gemini Audio / Whisper STT)"]
        Env_Engine["env_service.py\n(Microclimate Telemetry Client)"]
    end

    %% ────────────────────────────────────────────────────────────────
    %% PERSISTENCE & STORAGE TIER
    %% ────────────────────────────────────────────────────────────────
    subgraph PersistenceTier ["Persistence & File Storage Tier"]
        direction TB
        SQLite_DB[("plantiq_cleaned.db\n(SQLite Relational Store:\nusers, cache, chat, listings)")]
        PyTorch_Weights[("best_resnet50_coffee.pth\n(Fine-Tuned ResNet-50 Checkpoint)")]
        FAISS_Bin[("faiss_index.bin\n(FAISS IndexFlatIP Vectors)")]
        BM25_Pickle[("bm25_index.pkl\n(Rank-BM25 Inverted Index)")]
        Chunks_Pickle[("chunks.pkl\n(Document Chunk Store)")]
    end

    %% ────────────────────────────────────────────────────────────────
    %% EXTERNAL THIRD-PARTY CLOUD SERVICES
    %% ────────────────────────────────────────────────────────────────
    subgraph CloudTier ["External Cloud Services Tier (HTTPS / REST)"]
        direction TB
        OpenMeteo["Open-Meteo REST API\n(High-Res NWP & DEM Elevation)"]
        GeminiAPI["Google Generative AI\n(Gemini 2.5 Flash / 1.5 Audio)"]
        GroqAPI["Groq Cloud LPUs\n(Whisper Large-v3 / gpt-oss-120b)"]
        WhatsAppBridge["WhatsApp Business Protocol\n(wa.me URL Scheme)"]
        GoogleMapsBridge["Google Maps Navigation\n(maps.google.com Search Intent)"]
    end

    %% ────────────────────────────────────────────────────────────────
    %% INTER-TIER COMMUNICATION & PROTOCOLS
    %% ────────────────────────────────────────────────────────────────
    ClientTier -->|HTTP REST / JSON (Port 8000)\nAuthorization: Bearer JWT| GatewayTier
    GatewayTier --> APIRouter
    APIRouter --> AIServiceTier

    AIServiceTier --> SQLite_DB
    CNN_Engine --> PyTorch_Weights
    RAG_Engine --> FAISS_Bin
    RAG_Engine --> BM25_Pickle
    RAG_Engine --> Chunks_Pickle

    Env_Engine -->|HTTPS GET (Port 443)| OpenMeteo
    RAG_Engine -->|HTTPS POST (Port 443)| GeminiAPI
    Chat_Engine -->|HTTPS POST (Port 443)| GeminiAPI
    RAG_Engine -.->|Failover HTTPS POST| GroqAPI
    Chat_Engine -.->|Failover HTTPS POST| GroqAPI
    Voice_Engine -->|HTTPS POST (Port 443)| GroqAPI

    ClientTier -.->|Native OS Intent Handler| WhatsAppBridge
    ClientTier -.->|Native OS Intent Handler| GoogleMapsBridge
```

---

[MODULE: Packaging & Deployment | SECTION: 3.6 Packaging and Deployment Description | TYPE: Text]
Source: backend/run.py, mobile/capacitor.config.json, docs/architecture/06_MOBILE_EDGE_AND_SYSTEM_SECURITY.md

### 3.6.1 Deployment Architecture & Packaging Details

The PlantIQ deployment topology implements a distributed client-server architecture partitioned into five execution tiers:

1. **Client Tier (Presentation & Mobile Edge)**:
   - **Android Mobile Application**: Packaged as a standalone native APK (4.11 MB) via Capacitor 7. The native Android layer compiles `MainActivity.java` with API Level 34. The asset directory `mobile/android/app/src/main/assets/public` bundles the static HTML5, CSS3, and ES6 JavaScript assets. Cleartext network traffic is explicitly whitelisted in `network_security_config.xml` to allow communication with local development servers across Wi-Fi subnets.
   - **Web Browser Runtime**: Modern desktop and mobile browsers (Chrome, Safari, Firefox) consume semantic web pages rendered directly from FastAPI's static mount.
   - **In-App Dynamic Server IP Switcher**: The client-side runtime ([api.js](file:///d:/end-capstone-project/cleaned/frontend/static/js/api.js)) intercepts all outbound `fetch()` calls. A status ping loop (`GET /health`) displays server health (green/red dot), and the active backend endpoint is persisted dynamically in browser `localStorage.getItem('plantiq_server_url')`.

2. **Application Gateway & Web Server Tier**:
   - **FastAPI Core**: Hosted on Python 3.11 using the Uvicorn ASGI server running on `0.0.0.0:8000`.
   - **CORS Middleware**: Permissive CORS policy (`allow_origins=["*"]`) enabled to accommodate requests from `localhost`, local IP addresses, and Capacitor's internal WebView origins (`capacitor://localhost`, `http://localhost`).
   - **Authentication Middleware**: Stateless JWT authentication using HS256 signatures with 1440-minute (24-hour) expiration windows.

3. **Intelligent AI Services Tier**:
   - Co-located on the FastAPI application host to minimize network serialization overhead.
   - **PyTorch CNN Runtime**: Operates in evaluation mode (`eval()`) with multi-threaded CPU tensor execution.
   - **Vector & Lexical Search**: FAISS C++ binary flat vector index and Rank-BM25 memory-mapped lexical index.

4. **Persistence & Storage Tier**:
   - **Relational Store**: Embedded SQLite file database ([plantiq_cleaned.db](file:///d:/end-capstone-project/cleaned/backend/plantiq_cleaned.db)) with WAL journal mode.
   - **Vector Binary Checkpoints**: `faiss_index.bin` (768-dimensional normalized dense vectors).
   - **Neural Network Weights**: `best_resnet50_coffee.pth` (25.5 million parameter fine-tuned ResNet-50 state dictionary).

5. **External Cloud Services Tier**:
   - **Open-Meteo REST API**: Geospatial high-resolution NWP forecasts over TLS/HTTPS.
   - **Google Generative AI**: Gemini 2.5 Flash for multimodal reasoning and Kannada generation.
   - **Groq LPU Cloud**: Ultra-low-latency Whisper Large-v3 speech-to-text and `gpt-oss-120b` fallback inference.
   - **External App Intent Handshakes**: Direct OS-level intent dispatching to WhatsApp Business and Google Maps without web-based intermediaries.
