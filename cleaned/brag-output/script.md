# PlantIQ — Timestamped Narration Script & Visual Storyboard

## Overview
- **Total Duration**: 46.000 seconds (1,380 frames @ 30 fps)
- **Audio Profile**: Kokoro-82M AI voice (`af_heart`, speed multiplier 1.05)
- **Measured Speech Time**: 31.893 seconds
- **Music Bed**: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3` (ducked by -15 dB under narration)
- **Aspect Ratio**: 1920x1080 (16:9 Landscape)

---

## Timestamped Beat Sheet

### Scene 1: Hook — The Problem (0.000s – 5.200s)
- **Visuals (Left 55%)**: Kinetic typographic entry. "Coffee leaf diseases are hard to spot early. Expert help is hundreds of kilometers away."
- **Phone Mockup (Right 40%)**: Pixel-style frame enters with spring overshoot from right edge (soft shadow, subtle 3D tilt easing to flat). Displays real PlantIQ scanner home screen with green live server connection dot.
- **Audio Cue**:
  - `0.400s – 3.835s`: *"Coffee farmers lose crops to leaf disease they spot too late."* (`phrase_01_hook.wav`, 3.435s)
  - `4.000s – 5.216s`: *"Meet PlantIQ."* (`phrase_02_meet.wav`, 1.216s)
- **Subtitles (Left 55%, 64px bold)**:
  - `0.400s – 3.900s`: **Coffee farmers lose crops** to **leaf disease** spotted too late.
  - `4.000s – 5.200s`: Meet **PlantIQ**.

---

### Scene 2: Leaf Scan — ResNet-50 Classification (5.200s – 12.000s)
- **Visuals (Left 55%)**:
  - Headline: **Instant Leaf Diagnostics**
  - Subhead: "Fine-tuned Deep Residual CNN (25.5M parameters) trained on agricultural foliar datasets."
  - Tech Chips: `PyTorch ResNet-50` • `20ms Local Inference` • `Top-1 Accuracy 96.4%`
- **Phone Mockup (Right 40%)**:
  - `5.500s`: Farmer uploads coffee leaf photo (`rust_sample.jpg`). Preview loads with delete action.
  - `7.000s`: Classification triggers.
  - `8.200s`: Diagnosis card pops in with bounce: "Disease Detected", "Coffee Leaf Rust", 96.4% confidence gauge, class probability distribution bars (`Rust 96.4%`, `Cercospora 2.1%`, `Phoma 0.8%`, `Miner 0.5%`). Label beneath phone: *"CNN classification"*.
- **Audio Cue**:
  - `5.800s – 9.597s`: *"Scan a leaf, and a CNN identifies the disease in seconds."* (`phrase_03_scan.wav`, 3.797s)
- **Subtitles**:
  - `5.800s – 9.600s`: Scan a leaf, and a **CNN** identifies the disease in **seconds**.

---

### Scene 3: Treatment Advice — Hybrid RAG Pipeline (12.000s – 19.500s)
- **Visuals (Left 55%)**:
  - Dynamic 4-step architecture flow lines draw on sequentially:
    1. `Detected Disease` (*Hemileia vastatrix*)
    2. `Hybrid RAG Retrieval` (`BGE-Base` Dense + `BM25` Sparse + `ms-marco` Cross-Encoder Reranker)
    3. `LLM Rewrite` (`Google Gemini 2.5 Flash`)
    4. `Simple Field Advice` (CCRI dosages & cultural canopy shade practices)
- **Phone Mockup (Right 40%)**:
  - Shared-element morph into CCRI Treatment Advisory card:
    - Bordeaux mixture 1% foliar spray pre-monsoon (1 kg copper sulphate + 1 kg lime / 100 L water)
    - Bayleton 25 WP (160 g / barrel) / Contaf 5% EC post-monsoon
    - Shade tree thinning to 50–60% diffused sunlight
- **Audio Cue**:
  - `12.300s – 15.991s`: *"Then retrieval-augmented generation finds the right treatment,"* (`phrase_04_rag.wav`, 3.691s)
  - `16.300s – 18.881s`: *"and an LLM explains it in plain language."* (`phrase_05_llm.wav`, 2.581s)
- **Subtitles**:
  - `12.300s – 16.000s`: **Hybrid RAG** retrieves the verified CCRI treatment.
  - `16.300s – 19.000s`: An **LLM** explains it in **plain language**.

---

### Scene 4: Environmental Context — GPS Microclimate (19.500s – 25.500s)
- **Visuals (Left 55%)**:
  - Location pin and live telemetry data chips fly into the RAG stage:
    - `Elevation: 980 m`
    - `Humidity: 78.0 %`
    - `Temperature: 24.5 °C`
    - `Soil pH: 6.2`
  - Headline: **Advice Adapts to Local Conditions**
  - Subtext: "High humidity indicates accelerated spore germination. Spray windows adjust automatically."
- **Phone Mockup (Right 40%)**:
  - Phone displays Estate Microclimate Telemetry card with live Open-Meteo data for Chikkamagaluru coordinates (13.3161°N, 75.7720°E).
- **Audio Cue**:
  - `20.000s – 23.307s`: *"Using GPS, advice adapts to local conditions."* (`phrase_06_gps.wav`, 3.307s)
- **Subtitles**:
  - `20.000s – 23.500s`: Using **GPS**, advice adapts to **local microclimate**.

---

### Scene 5: Multilingual Chatbot & Voice Memory (25.500s – 32.500s)
- **Visuals (Left 55%)**:
  - Feature tags pulse with green accents:
    - `Kannada + English` (`ಕನ್ನಡ ಲಿಪಿ`)
    - `Bilingual Voice Input` (Gemini Audio + Groq Whisper)
    - `Persistent Session Memory` (SQLite + SQLAlchemy)
  - Headline: **Farmer-First Multimodal AI**
- **Phone Mockup (Right 40%)**:
  - Real chatbot screen (`chat.html`).
  - Attached leaf thumbnail with diagnostic context.
  - Farmer asks in Kannada: *"ಎಲೆಗಳ ಮೇಲೆ ಹಳದಿ ಚುಕ್ಕೆಗಳಿವೆ, ಯಾವ ಔಷಧಿ ಸಿಂಪಡಿಸಬೇಕು?"*
  - PlantIQ replies in respectful native Kannada with exact Bordeaux 1% and Bayleton CCRI protocols.
  - Active pulsing green microphone button.
- **Audio Cue**:
  - `26.000s – 29.541s`: *"Ask the chatbot anything, in Kannada or English, by voice,"* (`phrase_07_chat.wav`, 3.541s)
  - `29.900s – 31.713s`: *"and it remembers you across sessions."* (`phrase_08_memory.wav`, 1.813s)
- **Subtitles**:
  - `26.000s – 29.600s`: Ask the chatbot in **Kannada** or **English**, by **voice**.
  - `29.900s – 32.000s`: And it **remembers you** across sessions.

---

### Scene 6: Marketplace & Diagnostic History (32.500s – 39.500s)
- **Visuals (Left 55%)**:
  - Headline: **Direct Farm-to-Buyer Marketplace**
  - Tag: *"Direct from farmer to buyer, no middleman"*
  - Feature chips: `1-Tap Phone Call` • `Google Maps Estate Navigation` • `Zero Middleman Fees` • `Saved Scan History`
- **Phone Mockup (Right 40%)**:
  - `33.000s – 36.500s`: Marketplace screen (`marketplace.html`) with coffee crop lot cards (Arabica Parchment ₹420/kg, Robusta Cherry ₹210/kg), tap ripple on "Call Planter" and Maps pin.
  - `36.500s – 39.500s`: Scan History screen (`history.html`) with past scans archive and 3-second animated undo toast.
- **Audio Cue**:
  - `33.000s – 35.624s`: *"List your crops and sell directly, no middleman,"* (`phrase_09_market.wav`, 2.624s)
  - `35.900s – 37.756s`: *"with a direct call and a map pin."* (`phrase_10_contact.wav`, 1.856s)
  - `38.000s – 39.856s`: *"Every scan is saved in your history."* (`phrase_11_history.wav`, 1.856s)
- **Subtitles**:
  - `33.000s – 35.700s`: List your crops and sell **directly, no middleman**.
  - `35.900s – 37.800s`: With a **direct call** and a **map pin**.
  - `38.000s – 39.900s`: Every scan is saved in your **history**.

---

### Scene 7: System Architecture & Outro (39.500s – 46.000s)
- **Full Frame Visuals**:
  - Comprehensive end-to-end architecture diagram draws on:
    `Capacitor 7 Mobile App` $\longrightarrow$ `FastAPI Backend` $\longrightarrow$ `PyTorch ResNet-50` $\longrightarrow$ `3-Stage Hybrid RAG` $\longrightarrow$ `Google Gemini 2.5 Flash` $\longleftrightarrow$ `Open-Meteo GPS Engine`
  - Real technology badges: `PyTorch` • `FAISS` • `BGE-Base` • `BM25` • `Cross-Encoder` • `Capacitor 7` • `FastAPI`
  - Large title reveal: **PlantIQ** — Intelligent Coffee Agronomy Platform
  - Author & Project: **Jeel Nada** (with team Mohammed Ayaan, Nidhi N) • PES University
  - Repository link: **github.com/jeelnadaa/plantiq-capstone**
  - Held stable for > 3.5 seconds.
- **Audio Cue**:
  - `40.200s – 42.376s`: *"Built for farmers, powered by AI."* (`phrase_12_outro.wav`, 2.176s)
  - `42.400s – 46.000s`: Quiet musical outro with smooth fade.
- **Subtitles**:
  - `40.200s – 42.500s`: Built for **farmers**. Powered by **AI**.
