# 3. System architecture

## 3.1 Big picture
```mermaid
flowchart LR
    subgraph Phone["Android phone (APK) / browser"]
        UI[React app<br/>screens · i18n · theme]
        LS[(local storage<br/>server URL · tokens · prefs)]
    end
    subgraph Server["PlantIQ server (laptop or cloud)"]
        API[FastAPI REST API<br/>/api/v1]
        SEC[Security layer<br/>headers · rate limit · auth]
        CNN[Module 1<br/>ResNet-50]
        RAG[Module 2<br/>hybrid retriever + LLM]
        ENV[Module 2<br/>weather & risk]
        CHAT[Module 3<br/>chat orchestration]
        STT[Speech-to-text]
        MKT[Module 4<br/>marketplace]
        DB[(PostgreSQL / SQLite)]
        FS[(media files<br/>knowledge index)]
    end
    subgraph Cloud["External services"]
        OM[Open-Meteo]
        LLM[Gemini · Groq]
    end
    UI -- HTTPS/HTTP JSON + multipart --> SEC --> API
    API --> CNN & RAG & CHAT & MKT & STT & ENV
    CHAT --> CNN & RAG & ENV
    RAG --> LLM
    STT -.fallback.-> LLM
    ENV --> OM
    API --> DB & FS
```

**Principles**
- The phone is a thin client; all models run on the server, so cheap phones work and models can be upgraded without a new APK.
- The server URL is chosen at runtime → the same APK works with a laptop on farm Wi-Fi, a tunnel, or a cloud server.
- Every external dependency has a fallback: Gemini → Groq → offline guide; GPU → CPU; quality RAG models → balanced models;
  Postgres → SQLite; local speech models → cloud speech; no weather → explicit "unavailable" (never invented numbers).

## 3.2 Server layers
| Layer | Responsibility |
|---|---|
| ASGI security middleware | Request id, security headers (CSP etc.), 15 MB body limit, global per-IP rate limit, request logging |
| CORS | Allow-list of app origins (APK, web, LAN in development) |
| Routers (`api/`) | auth, users, predict, scans, chat, marketplace, media, voice, environment, system |
| Schemas (`schemas/`) | Pydantic validation and normalisation of every request/response |
| Services (`services/`) | CNN, RAG, LLM client, language router, advisory, environment, chat, voice, storage, auth sessions |
| Registry | Lazily creates each heavy model once (singleton); can swap in deterministic fakes for tests |
| Persistence | SQLAlchemy models; media files on disk; knowledge index (FAISS + JSON) |

Heavy models load **lazily** (first use) or at start with `--warm`. A request never imports a model twice.

## 3.3 Data model
```mermaid
erDiagram
    USER ||--o{ REFRESH_TOKEN : "signed-in devices"
    USER ||--o{ SCAN : owns
    USER ||--o{ CHAT_THREAD : owns
    CHAT_THREAD ||--o{ CHAT_MESSAGE : contains
    USER ||--o{ CROP_LISTING : sells
    CROP_LISTING ||--o{ LISTING_REPORT : "reported by"
    USER ||--o{ MEDIA_FILE : uploads
    USER ||--o{ AUDIT_EVENT : "security log"
    SCAN }o--|| MEDIA_FILE : photo
    CHAT_MESSAGE }o--o| MEDIA_FILE : photo
    USER {
        int id
        string username
        string phone
        string email
        string argon2_hash
        string language
        int failed_logins
        datetime locked_until
    }
    REFRESH_TOKEN {
        string sha256_hash
        string family_id
        string device
        datetime expires_at
        datetime rotated_at
        datetime revoked_at
    }
    SCAN {
        string disease
        float confidence
        json distribution
        json env_data
        text advisory
        json citations
        json safety_audit
        bool is_blended
        datetime deleted_at
    }
    CROP_LISTING {
        string title
        string variety
        float quantity
        string quantity_unit
        float quantity_kg
        float price
        string price_unit
        float price_per_kg
        float latitude
        float longitude
        json photos
    }
    ANALYSIS_CACHE {
        string sha256_key
        json result
    }
```
Notes: `deleted_at` on scans enables the 3-second undo (soft delete; purged after 24 h). `ANALYSIS_CACHE` stores diagnosis
results by SHA-256 of image + user + question + language so a repeated photo is answered instantly.

## 3.4 A request end to end — "Check this leaf"
```mermaid
sequenceDiagram
    participant A as App
    participant M as Middleware
    participant P as /predict
    participant G as Image guard
    participant C as Cache
    participant N as ResNet-50
    participant W as Weather
    participant R as Retriever
    participant L as LLM
    A->>M: POST multipart (photo, question, lang, lat/lng) + Bearer token
    M->>P: size ok, rate ok, headers added
    P->>P: verify JWT, session alive
    P->>G: magic bytes, ≤10 MB, ≤4096 px, strip EXIF/GPS, re-encode JPEG
    P->>C: SHA-256(image+user+question+lang)
    alt cache hit
        C-->>P: stored result
    else miss
        P->>N: 224×224 tensor → softmax over 5 classes
        P->>W: Open-Meteo (cached 60 s) → risk level, spray window
        P->>R: dense + BM25 → RRF → topic filter → rerank → MMR → top 3 passages
        P->>L: prompt (diagnosis + weather + passages + fenced question)
        L-->>P: advice (or offline guide)
        P->>P: dose audit against passages
    end
    P->>P: save photo + scan row
    P-->>A: JSON result
```
Measured on the development laptop (RTX 3070 Laptop GPU): CNN 5 ms (GPU) / 55 ms (CPU); retrieval ≈ 0.4 s; full diagnosis
≈ 6 s, dominated by the LLM call.

## 3.5 Deployment options
| Option | How | When |
|---|---|---|
| Laptop on farm Wi-Fi | `scripts\run_backend.bat` → phones use `http://<laptop-ip>:8000` | Field demos, co-operatives |
| Cloud VM with GPU/CPU | Docker image (`backend/Dockerfile`) behind a TLS reverse proxy | Many users, internet access |
| Quick public link | `cloudflared tunnel --url http://localhost:8000` | Testing from anywhere |

The server also serves the same web app at `/` so a browser can be used instead of the APK.

## 3.6 Configuration & resilience
All configuration is environment variables (`backend/.env`). Key switches: `RAG_PROFILE` (auto/quality/balanced),
`ML_DEVICE` (auto/cuda/cpu), `ENABLE_LOCAL_*_STT`, `CONFIDENCE_THRESHOLD_CNN` (75 %) and `_RAG` (0.60), rate limits, CORS,
`DATABASE_URL`. Production mode refuses to start with a weak secret key or wildcard CORS and hides the API docs.
