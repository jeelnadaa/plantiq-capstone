# 🌿 PlantIQ — Comprehensive System Architecture & Engineering Report

## Executive Summary
**PlantIQ** is an integrated precision coffee agronomy, computer vision, and market discovery system engineered specifically for smallholder coffee planters in Karnataka's Western Ghats region (Chikkamagaluru, Kodagu, Hassan).

The system addresses the three fundamental bottlenecks of tropical coffee cultivation:
1. **Foliar Pathology Identification**: Real-time diagnostic classification of foliar diseases using deep residual learning.
2. **Actionable Agronomic Advisory & Hallucination-Free LLM Retrieval**: Scientific disease management and chemical dosage recommendations via 3-Stage Hybrid RAG (BGE-Base Dense + BM25 Lexical + Cross-Encoder Reranking).
3. **P2P Decentralized Direct Market Access**: Direct farmer-to-buyer crop listing with GPS estate spatial routing and native WhatsApp business negotiation.

---

## 🏛️ End-to-End System Topology

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PRESENTATION LAYER                                      │
│                                                                                         │
│   [ PlantIQ Mobile APK (Capacitor 7) ]          [ Desktop & Safari PWA (HTML5/CSS) ]   │
│   - Safe Area Insets (Notch & Bottom Bar)       - Responsive Mobile-First Viewport      │
│   - Hardware Back Button & Modal Interceptor    - Bilingual English / Kannada UI        │
│   - Dynamic Server IP Switcher & Ping Mon       - Multi-Photo Galleries & Camera Access │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │ REST / JSON (JWT Bearer Auth)
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  FASTAPI BACKEND                                        │
│                                                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                              SECURITY & CORE ROUTING                            │   │
│   │   - PBKDF2 Password Hashing (100k iters)   - Stateless JWT Token (HS256)        │   │
│   │   - CORS Multi-Origin Middleware           - SQLite Relational Database         │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                            │                                            │
│   ┌────────────────────────────────────────┴────────────────────────────────────────┐   │
│   │                           INTELLIGENT AI SERVICES LAYER                         │   │
│   │                                                                                 │   │
│   │   [ Module 1: Computer Vision (CNN) ]      [ Module 2: Hybrid RAG Engine ]      │   │
│   │   - ResNet-50 Deep Residual Network        - BAAI/bge-base-en-v1.5 (Dense)      │   │
│   │   - Softmax Temperature Calibration        - BM25Okapi Lexical Inverted Index   │   │
│   │   - SHA-256 Offline Image Cache            - ms-marco-MiniLM-L-6-v2 Reranker    │   │
│   │                                            - Sigmoid Score Normalization        │   │
│   │                                                                                 │   │
│   │   [ Module 3: Multimodal Chatbot ]         [ Module 4: Microclimate Engine ]    │   │
│   │   - Bilingual Linguistic Pre-Router        - Open-Meteo High-Resolution NWP     │   │
│   │   - Sequential Diagnostic Context Fusion   - Elevation & DEM Topography         │   │
│   │   - Gemini 2.5 Flash / Groq LLaMA Failover - Fungal Spore Germination Risk Idx  │   │
│   │   - Persistent Base64 Image History        - Spray Window Optimization          │   │
│   │                                                                                 │   │
│   │   [ Module 5: Spatial Marketplace ]        [ Module 6: Mobile Edge Bridge ]     │   │
│   │   - P2P Crop Listings & Multi-Photos       - Android Native Intents (WhatsApp)  │   │
│   │   - Haversine Distance Geo-Querying        - Google Maps Intent Dispatch        │   │
│   │   - Direct Telephony & WhatsApp Bridge     - Cleartext Network Security Config  │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📑 Detailed Architectural Modules Reference

| Module | Document Link | Core Technologies & Models |
| :--- | :--- | :--- |
| **Module 1: Leaf Pathology CNN** | [01_CNN_DIAGNOSTICS_MODULE.md](file:///d:/end-capstone-project/cleaned/docs/architecture/01_CNN_DIAGNOSTICS_MODULE.md) | PyTorch, ResNet-50, AdamW, Cosine Annealing, SHA-256 Caching |
| **Module 2: Advanced Hybrid RAG** | [02_ADVANCED_HYBRID_RAG_MODULE.md](file:///d:/end-capstone-project/cleaned/docs/architecture/02_ADVANCED_HYBRID_RAG_MODULE.md) | `bge-base-en-v1.5`, FAISS IndexFlatIP, BM25Okapi, Cross-Encoder, Sigmoid Normalization |
| **Module 3: Multimodal Chatbot** | [03_MULTIMODAL_CHATBOT_AND_ROUTING.md](file:///d:/end-capstone-project/cleaned/docs/architecture/03_MULTIMODAL_CHATBOT_AND_ROUTING.md) | Linguistic Router, Kanglish Translation, Gemini 2.5 Flash, Groq LLaMA-3.3-70B, SQLite Image Storage |
| **Module 4: Microclimate Risk Engine** | [04_MICROCLIMATE_RISK_ENGINE.md](file:///d:/end-capstone-project/cleaned/docs/architecture/04_MICROCLIMATE_RISK_ENGINE.md) | Open-Meteo API, ERA5 Reanalysis, DEM Elevation, Epidemiological Risk Formulation |
| **Module 5: Spatial Marketplace** | [05_MARKETPLACE_AND_SPATIAL_DISCOVERY.md](file:///d:/end-capstone-project/cleaned/docs/architecture/05_MARKETPLACE_AND_SPATIAL_DISCOVERY.md) | Haversine Distance, Native Intents, Google Maps, Multi-Photo Storage |
| **Module 6: Mobile Edge & Security** | [06_MOBILE_EDGE_AND_SYSTEM_SECURITY.md](file:///d:/end-capstone-project/cleaned/docs/architecture/06_MOBILE_EDGE_AND_SYSTEM_SECURITY.md) | Capacitor 7, PBKDF2 Password Hashing, JWT Bearer Tokens, Dynamic Server Switching |
| **🎓 Academic Defense Guide** | [07_PROFESSOR_DEFENSE_AND_CROSS_EXAMINATION_GUIDE.md](file:///d:/end-capstone-project/cleaned/docs/architecture/07_PROFESSOR_DEFENSE_AND_CROSS_EXAMINATION_GUIDE.md) | Strict Technical Defense Q&A, Mathematical Proofs, and Architectural Rationale |
