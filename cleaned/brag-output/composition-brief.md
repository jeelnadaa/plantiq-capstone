# Hyperframes Composition Brief: PlantIQ

## Objective
Create a high-impact, launch-grade portfolio video for PlantIQ, an intelligent coffee agronomy platform built for coffee farmers in Karnataka, India.

## Output Specifications
- **Composition Directory**: `brag-output/composition/`
- **Rendered Video**: `brag-output/brag.mp4`
- **Poster Still**: `brag-output/brag.jpg` (baked into frame 0 of MP4)
- **Format**: Landscape 16:9 (1920x1080)
- **Framerate**: 30 fps constant
- **Duration**: 46.00 seconds (1,380 frames)

## Source Material
- **Project Root**: `d:/end-capstone-project/cleaned`
- **Application Name**: PlantIQ
- **Author**: Jeel Nada (PES University)
- **GitHub**: `https://github.com/jeelnadaa/plantiq-capstone.git`
- **Target Audience**: Coffee farmers in Karnataka, plantation managers, agricultural buyers, technical evaluators, hiring managers.
- **Key Claims & Real Tech**:
  - PyTorch ResNet-50 leaf disease classifier (96.4% Top-1 accuracy, 20ms local inference).
  - 3-Stage Production Hybrid RAG (BGE-Base Dense + BM25 Lexical + Cross-Encoder Reranker, 94.7% Precision@3).
  - Open-Meteo GPS Microclimate Risk Engine (Elevation, Humidity, Temperature, Rainfall, Soil pH).
  - Bilingual Multimodal Voice Chatbot (Native Kannada script `ಕನ್ನಡ ಲಿಪಿ` & English, persistent session memory).
  - Direct Crop Marketplace (Farmer-to-buyer direct call and Google Maps estate pin, 0% middleman fees).
  - Scan History with 3-second animated undo toast.

## Creative Direction
- **Tone Preset**: `polished` / `clean, calm, trustworthy`
- **Creative Direction**: Clean, calm, trustworthy. Light off-white background (`#fbf9f4`), one restrained green accent (`#15803d` / `#16a34a`), big readable typography (Plus Jakarta Sans), smooth spring motion. Warm but professional, like a polished product launch for a real-world impact app.
- **Layout Rule**:
  - Text block on the left 55%, left-aligned, vertically centered, with 120px margins. Nothing within 90px of any edge. Subtitles never overlap the phone.
  - Subtitles minimum 64px bold, maximum 2 lines and 4-6 words per line, shown phrase by phrase as spoken with key words highlighted.
  - Flow labels and tech chips at least 36px with high contrast.
  - Right 40%: Android phone mockup (Pixel-style frame with punch-hole camera and soft drop shadow, subtle 3D tilt easing to flat). Displays real app screens captured from the actual APK codebase.

## Audio Specifications
- **Audio Role**: Warm, grounded narration with gentle music bed and crisp UI accents.
- **Speech**: Kokoro-82M AI narration (`af_heart`, 31.89s spoken time across 12 phrases).
- **Music Bed**: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3` ducked by -15 dB under narration.
- **SFX**: Subtle UI pops and click accents at scene transitions and node unlocks.
- **Audio-Visual Sync**: Every phrase, subtitle, and visual beat is derived from ffprobe measurements of generated narration clips within 100ms tolerance.

## Storyboard Scenes
1. **Scene 1 (0.0s – 5.2s)**: Hook — The Problem. Phone enters with spring ease. Scanner ready.
2. **Scene 2 (5.2s – 12.0s)**: Leaf Scan — Farmer photo loaded. CNN identifies disease in seconds. Label: "CNN classification".
3. **Scene 3 (12.0s – 19.5s)**: Advice — CCRI Treatment Advice screen. 4-step flow animates on left.
4. **Scene 4 (19.5s – 25.5s)**: Local Context — GPS microclimate telemetry chips animate into RAG step.
5. **Scene 5 (25.5s – 32.5s)**: Chatbot — Kannada + English multimodal voice chatbot in phone with persistent memory.
6. **Scene 6 (32.5s – 39.5s)**: Marketplace & History — Direct farm listings, call & map pin actions, scan history feed.
7. **Scene 7 (39.5s – 46.0s)**: Architecture & Close — Full-frame system diagram draws on, real tech badges, Jeel Nada, and GitHub repository held stable until 46.0s.
