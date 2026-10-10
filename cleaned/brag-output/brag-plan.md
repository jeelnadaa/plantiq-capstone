# PlantIQ — Launch Video Production Plan

## Planning Rubric & Creative Angle
1. **Who is the app for?**
   Coffee farmers and agricultural buyers in Karnataka, India (specifically the Kodagu, Chikkamagaluru, and Hassan coffee agroforestry belt).
2. **What problem does it solve?**
   Coffee leaf rust and foliar diseases are hard to detect early in estate fields, while expert agronomic assistance and extension centers are geographically distant. Intermediaries additionally extract high margins from coffee trade.
3. **What is the product's core mechanism?**
   A native mobile app combining on-device/fast-API leaf pathology CNN classification, 3-Stage Hybrid RAG grounded in authoritative Central Coffee Research Institute (CCRI) literature, real-time GPS microclimate weather risk telemetry, a persistent bilingual Kannada/English voice chatbot, and a direct farmer-to-buyer crop marketplace.
4. **What real tech powers it?**
   PyTorch ResNet-50 (25.5M params, 96.4% accuracy), BAAI/bge-base-en-v1.5 dense bi-encoder, FAISS IndexFlatIP, BM25Okapi lexical retriever, cross-encoder/ms-marco-MiniLM-L-6-v2 deep reranker, Google Gemini 2.5 Flash, Open-Meteo microclimate API, Capacitor 7 native Android container, FastAPI backend, SQLite persistent memory.
5. **What is the creative angle?**
   "Clean, calm, trustworthy product launch for real-world impact." The video speaks directly to recruiters, hiring managers, and engineers. It balances human impact (empowering smallholder coffee farmers) with rigorous deep-tech architecture.
6. **What is the visual aesthetic?**
   Light off-white background (`#fbf9f4`), crisp near-black typography, one restrained emerald green accent (`#15803d` / `#16a34a`), smooth spring physics with overshoot, an authentic Android Pixel mockup frame with punch-hole camera and soft 3D elevation, and 100% real app screens captured directly from the APK source.
7. **What is the narrative arc?**
   The Problem (farmers lose crops) $\to$ The Scan (instant CNN identification) $\to$ The Advisory (3-stage Hybrid RAG + CCRI dosages) $\to$ Local Microclimate Context (GPS elevation & humidity adaptation) $\to$ Bilingual Voice Chatbot (Kannada + English memory) $\to$ Direct Marketplace & History (0% middleman fees, saved scans) $\to$ Full Architecture & Author Outro.
8. **What is the audio strategy?**
   Kokoro-82M AI voiceover (`af_heart`, warm and steady) measured clip-by-clip with ffprobe, synchronized within 100ms with animated typography. Quiet background music (`happy-beats-vol-12`) ducked by -15 dB under speech.
9. **How is success measured?**
   In 46 seconds, any viewer clearly understands who the app helps, what it does in the field, and the exact software and AI architecture powering it.

---

## Music Cue Guidance
- **Track**: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3`
- **Volume Posture**: 0.15 master gain during narration (-15 dB ducking), swelling gently during scene transitions and final outro hold.
- **Audio-Reactive Treatment**: Subtle RMS warmth applied to the green active node glow and phone elevation shadow.

---

## Storyboard & Timing
- Total Duration: 46.00s (1,380 frames @ 30 fps)
- Scene 1: Hook (0.0s – 5.2s)
- Scene 2: Scan (5.2s – 12.0s)
- Scene 3: Advice (12.0s – 19.5s)
- Scene 4: Local Context (19.5s – 25.5s)
- Scene 5: Chatbot (25.5s – 32.5s)
- Scene 6: Marketplace & History (32.5s – 39.5s)
- Scene 7: Architecture & Close (39.5s – 46.0s)
