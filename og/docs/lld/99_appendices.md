# Appendices
## Low Level Design Document – Appendices A to D

[MODULE: Appendices | SECTION: Appendix A: Definitions, Acronyms and Abbreviations | TYPE: Table]
Source: docs/architecture/00_SYSTEM_ARCHITECTURE_OVERVIEW.md, README.md

### Appendix A: Definitions, Acronyms, and Abbreviations

| Term / Acronym | Definition |
| :--- | :--- |
| **API** | Application Programming Interface |
| **APK** | Android Package Kit (native installable Android application archive) |
| **BGE** | BAAI General Embedding (state-of-the-art dense semantic bi-encoder vector model) |
| **BM25** | Best Matching 25 (Okapi BM25 non-linear term frequency/inverse document frequency probabilistic retrieval algorithm) |
| **CCRI** | Central Coffee Research Institute (Balehonnur, Chikkamagaluru, Karnataka) |
| **CNN** | Convolutional Neural Network |
| **Cross-Encoder**| Transformer architecture scoring query and document simultaneously across all cross-attention heads |
| **CUDA** | Compute Unified Device Architecture (NVIDIA parallel computing platform) |
| **DEM** | Digital Elevation Model (topographical elevation data above sea level) |
| **FAISS** | Facebook AI Similarity Search (library for dense vector clustering and similarity search) |
| **HLD** | High-Level Design Document |
| **HS256** | HMAC using SHA-256 cryptographic algorithm for signing stateless JSON Web Tokens |
| **JWT** | JSON Web Token (RFC 7519 compact URL-safe authentication token) |
| **LLD** | Low-Level Design Document |
| **LLM** | Large Language Model |
| **LPU** | Language Processing Unit (Groq custom micro-architecture for high-throughput tensor inference) |
| **NWP** | Numerical Weather Prediction |
| **ORM** | Object-Relational Mapping (declarative persistence layer via SQLAlchemy) |
| **P2P** | Peer-to-Peer (decentralized direct trading network between producers and buyers) |
| **PBKDF2** | Password-Based Key Derivation Function 2 (RFC 2898 cryptographic key derivation with 100,000 rounds) |
| **RAG** | Retrieval-Augmented Generation |
| **ResNet-50** | 50-layer Deep Residual Network utilizing shortcut identity skip-connections |
| **SHA-256** | Secure Hash Algorithm 256-bit (cryptographic deterministic digest) |
| **SRS** | Software Requirements Specification |
| **STT** | Speech-to-Text (automated voice transcription) |
| **TTFT** | Time to First Token (latency metric for generative AI token streaming) |
| **WAL** | Write-Ahead Logging (SQLite high-concurrency database journal mode) |

---

[MODULE: Appendices | SECTION: Appendix B: References | TYPE: Table]
Source: docs/architecture/, backend/requirements.txt

### Appendix B: References

| Reference ID | Title / Document | Author(s) / Organization | Year / Version | Description |
| :--- | :--- | :--- | :--- | :--- |
| **REF-01** | *Deep Residual Learning for Image Recognition* | K. He, X. Zhang, S. Ren, J. Sun (CVPR) | 2016 | Foundation paper establishing residual skip-connections and ResNet-50 architecture. |
| **REF-02** | *C-Pack: Packaged Resources to Advance General Chinese and Multilingual Embedding* | S. Xiao, et al. (BAAI) | 2023 | Specification of `BAAI/bge-base-en-v1.5` dense text embedding model. |
| **REF-03** | *The Probabilistic Relevance Framework: BM25 and Beyond* | S. Robertson, H. Zaragoza | 2009 | Theoretical foundation for BM25Okapi inverted index term frequency retrieval. |
| **REF-04** | *Coffee Cultivation Guide & Integrated Foliar Disease Management Protocols* | Central Coffee Research Institute (CCRI), Balehonnur | 2022 | Official agronomic extension recommendations for Arabica and Robusta cultivation. |
| **REF-05** | *FastAPI Modern Python Web Framework Specification* | S. Ramírez | 2024 / v0.110 | Standard documentation for asynchronous ASGI routing, dependency injection, and Pydantic validation. |
| **REF-06** | *Capacitor 7 Native Android Bridge Specification* | Ionic Framework Team | 2024 / v7.0 | Technical specifications for hybrid web view asset packaging, safe area insets, and native intents. |
| **REF-07** | *Open-Meteo High-Resolution Weather & Elevation API Reference* | Open-Meteo GmbH | 2024 | Specification for real-time NWP temperature, humidity, rainfall, and DEM altitude endpoints. |
| **REF-08** | *RFC 7519: JSON Web Token (JWT)* | Internet Engineering Task Force (IETF) | 2015 | Standard defining URL-safe, digitally signed claims representation. |

---

[MODULE: Appendices | SECTION: Appendix C: Record of Change History | TYPE: Table]
Source: git log, README.md, docs/architecture/00_SYSTEM_ARCHITECTURE_OVERVIEW.md

### Appendix C: Record of Change History

| # | Date | Document Version No. | Change Description | Reason for Change |
| :--- | :--- | :--- | :--- | :--- |
| **1** | 2026-08-15 | v0.1 | Initial System Requirements and Architectural Baseline | Capstone Phase 1 initiation and problem formulation. |
| **2** | 2026-09-01 | v1.0 | High-Level Design (HLD) and Modular Decomposition | Definition of ResNet-50 vision classifier, RAG pipeline, and P2P marketplace. |
| **3** | 2026-09-18 | v1.5 | Transition to 3-Stage Hybrid RAG and Multi-turn SQLite Chat Persistence | Addressing vocabulary mismatch on chemical dosages and ensuring cross-page photo rehydration. |
| **4** | 2026-09-25 | v1.9 | Integration of Capacitor 7 Mobile APK and Dynamic Server IP Switcher | Elimination of hardcoded IP addresses for resilient live demonstration in mobile Wi-Fi environments. |
| **5** | 2026-09-28 | v2.0 | Comprehensive Low-Level Design (LLD) Document Specification | Final Phase 3 documentation adhering to university academic template standards. |

---

[MODULE: Appendices | SECTION: Appendix D: Traceability Matrix | TYPE: Table]
Source: docs/architecture/00_SYSTEM_ARCHITECTURE_OVERVIEW.md, docs/lld/

### Appendix D: Traceability Matrix

| Requirement ID & Functional Description | HLD Reference Section & Architecture Component | LLD Document Reference Section & Concrete Implementation |
| :--- | :--- | :--- |
| **REQ-01: Leaf Pathology Computer Vision**<br>Automated classification of Rust, Cercospora, Miner, Phoma, and Healthy states. | HLD §3.1 Computer Vision Subsystem<br>`01_CNN_DIAGNOSTICS_MODULE.md` | LLD §3.2 Module 1 (`01_leaf_pathology_cnn.md`)<br>`CNNModelWrapper.predict()` in `cnn_service.py` |
| **REQ-02: Deterministic Diagnostic Caching**<br>SHA-256 deduplication to eliminate redundant neural inference on identical photos. | HLD §3.1.2 Offline Deduplication Cache<br>`01_CNN_DIAGNOSTICS_MODULE.md` | LLD §3.2 Module 1 (`01_leaf_pathology_cnn.md`)<br>`compute_image_hash()`, `ImageAnalysisCache` |
| **REQ-03: 3-Stage Hybrid Agronomic RAG**<br>Dense vector search combined with sparse lexical search and cross-encoder reranking. | HLD §3.2 Hybrid RAG Engine<br>`02_ADVANCED_HYBRID_RAG_MODULE.md` | LLD §3.3 Module 2 (`02_hybrid_rag_advisory.md`)<br>`RAGService.search()` in `rag_service.py` |
| **REQ-04: Sigmoid Score Normalization**<br>Non-linear mapping of reranker logits to $[0, 1]$ interval for stable confidence gating. | HLD §3.2.4 Normalization Formulation<br>`02_ADVANCED_HYBRID_RAG_MODULE.md` | LLD §3.3 Module 2 (`02_hybrid_rag_advisory.md`)<br>`RAGService.search()` lines 180–182 |
| **REQ-05: Bilingual Linguistic Pre-Routing**<br>Sub-millisecond classification of Kannada, Kanglish, and English with keyword translation. | HLD §3.3 Linguistic Pre-Router<br>`03_MULTIMODAL_CHATBOT_AND_ROUTING.md` | LLD §3.4 Module 3 (`03_multimodal_chat_routing.md`)<br>`analyze_and_route_query()` in `router_service.py` |
| **REQ-06: Multimodal Chat & Image Memory**<br>Persistent dialogue threads with base64 leaf photo rehydration and Gemini/Groq orchestration. | HLD §3.3 Multimodal Dialogue System<br>`03_MULTIMODAL_CHATBOT_AND_ROUTING.md` | LLD §3.4 Module 3 (`03_multimodal_chat_routing.md`)<br>`ChatThread`, `ChatMessage`, `process_chat_message()` |
| **REQ-07: Voice Audio Transcription**<br>Multilingual speech query transcription in native Kannada and English. | HLD §3.3 Voice Subsystem<br>`03_MULTIMODAL_CHATBOT_AND_ROUTING.md` | LLD §3.4 Module 3 (`03_multimodal_chat_routing.md`)<br>`transcribe_audio()` in `voice_service.py` |
| **REQ-08: Geospatial Microclimate Risk Modeling**<br>Ingestion of Open-Meteo weather telemetry and calculation of fungal spore germination index. | HLD §3.4 Microclimate Risk Engine<br>`04_MICROCLIMATE_RISK_ENGINE.md` | LLD §3.5 Module 4 (`04_microclimate_marketplace.md`)<br>`EnvironmentalService.get_environmental_data()` |
| **REQ-09: Direct P2P Crop Marketplace**<br>Lot-level crop listing publication with multi-photo galleries, search filters, and ownership controls. | HLD §3.5 Spatial Marketplace<br>`05_MARKETPLACE_AND_SPATIAL_DISCOVERY.md` | LLD §3.5 Module 4 (`04_microclimate_marketplace.md`)<br>`CropListing`, `api/marketplace.py` |
| **REQ-10: Native Mobile Intent Handshakes**<br>1-tap Google Maps estate routing and WhatsApp business communication via Android OS intents. | HLD §3.5.2 Intent Bridge Protocol<br>`05_MARKETPLACE_AND_SPATIAL_DISCOVERY.md` | LLD §3.5 Module 4 (`04_microclimate_marketplace.md`)<br>`format_listing_response()` in `marketplace.py` |
| **REQ-11: Mobile Edge & System Security**<br>Capacitor 7 APK runtime, PBKDF2 password hashing, and dynamic server IP switching. | HLD §3.6 Mobile Edge & Security<br>`06_MOBILE_EDGE_AND_SYSTEM_SECURITY.md` | LLD §3.6 Packaging (`05_packaging_deployment.md`)<br>`security.py`, `capacitor.config.json`, `api.js` |
