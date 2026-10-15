# PlantIQ Mobile Design System (A/B Test Variant B)

Generated using **figcraft-cli** for smallholder coffee planters in Karnataka (Chikkamagaluru, Kodagu, Hassan).

---

## 1. Executive Summary & Design Rationale

### Target User Persona
- **Persona**: Indian coffee planters / farm supervisors in Western Ghats, Karnataka.
- **Field Conditions**: Outdoor sunlight, dirty or gloved fingers, intermittent rural 4G connectivity, varied digital literacy.
- **Language**: Bilingual (Kannada script ಕನ್ನಡ + English).
- **Aesthetics Philosophy**: 
  - **No Neo-Brutalism**: Avoids harsh high-contrast black borders, stark monospace styling, or cold industrial motifs.
  - **Organic & Tactile Agronomy**: Deep forest emerald `#134e35`, warm clay/terracotta `#c86a3b`, sun gold `#e6a817`, and soft cream/card surfaces (`#fcfbf7` / `#ffffff`).
  - **Outdoor Legibility & Ergonomics**: High-contrast typography (Inter / Noto Sans Kannada), minimum 52px touch targets for thumb navigation, high-visibility status badges, audio-first voice interactions.

---

## 2. Comprehensive Backend Functional Coverage

Every single backend API capability and model from the PlantIQ backend (`/backend/app/api`) is mapped to an interactive UI pattern:

| # | Backend Module | API Endpoints & Models | Mobile Screen & Functional UI Elements |
|---|---|---|---|
| **1** | **Computer Vision Diagnostic** | `POST /api/predict`<br>`models/resnet50_best.pth`<br>`models/scaler.pkl` | **Screen 01 & 02**: Camera viewfinder with alignment reticle, flash toggle, gallery upload, instant confidence badge (94.8%), multi-class probability breakdown (Leaf Rust, Cercospora, Phoma, Healthy). |
| **2** | **Microclimate Weather Engine** | `GET /api/environment?lat=...&lng=...`<br>`GET /api/environment/forecast`<br>Open-Meteo Integration | **Screen 01 & 02**: Dual GPS/manual coordinate ingestion, live weather chip (`24.2°C (Feels 26.5°C), 84% RH, 0.0mm rain, 1,150m ASL`), Coffee Rust Incubation Index (`HIGH RISK`), 48-hour preventive spray window indicator, zero-mock fallback. |
| **3** | **3-Stage Hybrid RAG Advisory** | `POST /api/chat`<br>`app/services/hybrid_rag.py`<br>BM25 + Dense + Cross-Encoder Reranker | **Screen 02 & 03**: Certified CCRI (Central Coffee Research Institute) treatment prescription, structured chemical vs organic spray schedule, safety guardrails badge (`Verified Safe Dosage - CIBRC Compliant`), exact source citations (`CCRI Coffee Guide 8th Ed. pg. 42`). |
| **4** | **Multimodal Bilingual Chat** | `POST /api/chat`<br>`POST /api/voice/transcribe`<br>`AI4Bharat IndicConformer` | **Screen 03**: Bilingual conversation history (Kannada & English), attached leaf diagnostic snapshot, in-chat manual location controls with live microclimate chip (`📍 12.4244°N, 75.7382°E • 23.1°C`), wave-audio player, prominent voice microphone. |
| **5** | **Coffee Lot Marketplace** | `GET /api/marketplace/lots`<br>`GET /api/marketplace/lots/{id}`<br>`GET /api/marketplace/my-listings` | **Screen 04**: Dual segmented tabs ("Browse Lots" vs "My Listings"), search bar, cultivar filters (Arabica Selection 795, Robusta CxR, Mysore Banana), parchment & cherry price cards (₹9,800 / 50kg bag), Direct 1-tap WhatsApp and Phone inquiry buttons. |
| **6** | **Lot Creation & GPS Geo-tag** | `POST /api/marketplace/lots`<br>Multi-photo upload & GPS metadata | **Screen 05**: 4-slot photo upload grid with cover indicator, radio toggles for Arabica/Robusta and Parchment/Cherry, moisture slider (10.5%), GPS auto-fetch tag (`Chikkamagaluru • 13.31°N, 75.77°E`), WhatsApp contact toggle, instantaneous estimated lot value calculator. |
| **7** | **Scan History & Health Tracking** | `GET /api/history`<br>`DELETE /api/history/{id}` (with undo) | **Screen 06**: Chronological disease timeline, severity tags (Active/Treated/Monitoring), printable CCRI advisory download link, quick-scan CTA, undo deletion action toast. |
| **8** | **Dynamic Server Switching & Profile** | `GET /api/health`<br>Live Ping & IP Configuration | **Screen 01 & 06**: Live ping indicator (`● Live (42ms)`), Server IP modal switcher for switching between local Wi-Fi and production cloud backends. |

---

## 3. Screen Inventory & Visual Architecture

All mobile screens are built for a standard **390 × 844 px** viewport (iPhone 14 / modern Android flagship standards) with 24px column margins and 16px element spacing.

### Screen 01: Leaf Scanner & Outbreak Radar (`01_Leaf_Scanner_Home.png`)
- **Top Bar**: Planter location ("Kalledevarapura Estate, Chikkamagaluru"), Kannada/English quick toggle, notification bell.
- **Microclimate Weather Strip**: Dual GPS/manual coordinates (`📍 Chikkamagaluru 13.3161°N, 75.7720°E`), current temp (`24.2°C`), apparent feels-like (`26.5°C`), humidity (`84%`), elevation (`1,150m ASL`), and real-time backend ping (`● Live 14ms`).
- **Camera Viewfinder**: Organic corner reticles, framing guidelines, live camera feed simulation, shutter button with leaf glow, album upload shortcut.
- **Regional Outbreak Warning**: High-visibility yellow banner alerting nearby farms of Coffee Leaf Rust spore activity.
- **Bottom Navigation Dock**: 5 primary thumb tabs (Scan, History, Chat, Market, Profile).

### Screen 02: Diagnosis & CCRI Treatment Advisory (`02_Diagnosis_Advisory.png`)
- **Diagnostic Header**: High-resolution leaf macro view with bounding boxes and 94.8% detection confidence badge.
- **Disease Probability Spectrum**: Visual progress bars showing relative probabilities for Coffee Leaf Rust, Cercospora Spot, and Phoma Blight.
- **Microclimate Vulnerability Matrix**: Real-time correlation with 88% humidity showing fungal incubation conditions.
- **CCRI Certified Prescription**: Two clear dosage cards:
  - *Immediate Action*: 0.5% Bordeaux Mixture formulation instructions.
  - *Curative Spray*: Hexaconazole 5% EC at 2ml/L dilution.
- **Verified Dosage Shield**: Green verification badge referencing Central Insecticides Board & Registration Committee (CIBRC) compliance.
- **RAG Provenance**: Footnote citing official CCRI advisory manuals with page reference.
- **Action CTAs**: Primary "Consult AI Agronomist" and secondary "Save to Farm History".

### Screen 03: Multimodal Bilingual Chatbot (`03_Bilingual_Chatbot.png`)
- **Top Navigation**: AI Agronomist persona card with IndicConformer active indicator.
- **Chat Transcript**:
  - Attached leaf diagnosis thumbnail with condition summary.
  - Farmer query in Kannada script: *"ಎಲೆ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಬೋರ್ಡೋ ಮಿಶ್ರಣ ಹೇಗೆ ಸಿಂಪಡಿಸಬೇಕು?"* (How should I spray Bordeaux mixture for leaf rust?).
  - AI agronomist voice note with playable audio waveform and timestamp.
  - Structured text response detailing morning spraying schedule and wet leaf precautions.
- **Multimodal Bottom Bar**: Attachment camera icon, expandable text input, and prominent green microphone button with audio recording state.

### Screen 04: Coffee Lot Marketplace (`04_Coffee_Marketplace.png`)
- **Header & Search**: Real-time coffee price index ticker (Arabica Parchment ₹9,800/bag), search field with quick chips (Parchment, Cherry, Micro-lot, Organic).
- **Segmented View**: Quick toggle between "Browse Lots" and "My Listings".
- **Farmer Lot Cards**:
  - High-res lot photo preview with batch tag ("Parchment Grade A").
  - Cultivar info, elevation (1,150m MSL), processing method, and moisture percentage (10.5%).
  - Estate location badge and bag count (45 Bags • 50kg each).
  - Prominent price breakdown and total lot value (₹4,41,000).
  - Quick action buttons: WhatsApp direct chat and phone call buttons.
- **Floating Action Button**: "+ List Coffee Lot" button in deep terracotta.

### Screen 05: Create Lot Listing (`05_Create_Lot_Listing.png`)
- **Media Upload**: 4-slot image uploader with visual upload triggers and cover badge.
- **Coffee Spec Form**:
  - Segmented selector for Arabica vs Robusta.
  - Processing type: Washed Parchment vs Sun-dried Cherry.
  - Variety input (Selection 795) and Grade picker (Plantation A).
- **Economics & Inventory**:
  - Bag count input (50kg bags) and price per bag input.
  - Live calculated lot gross value indicator.
- **GPS Location Tag**: Auto-captured geolocation chip with coordinate preview.
- **Buyer Contact Privacy**: Toggle for direct WhatsApp buyer inquiries.
- **Action**: High-emphasis "Publish to Coffee Marketplace" button.

### Screen 06: Farm Profile & Scan History (`06_History_and_Profile.png`)
- **Planter Profile Card**: Estate name, planter avatar, verified grower badge, and bilingual language toggle.
- **Seasonal KPIs**: Total Scans (48), Healthy Yield Index (92%), Active Treatments (2).
- **Scan Timeline**: Chronological history cards showing scan date, diagnosed leaf disease, treatment status tag, and action menus.
- **Undo Deletion Banner**: Safety bar allowing restoration of recently removed scans.
- **System Settings**: Dynamic Server IP configuration card with backend health ping.

---

## 4. Generated Artifacts & File Inventory

All generated artifacts are located in this folder:

```
figma-design/
├── plantiq_mobile_v2.fig           <-- Native Figma file (Import directly into Figma)
├── plantiq_mobile_redesign.figcraft<-- Native Figcraft document file
├── all_screens_preview.png         <-- High-resolution canvas preview of all 6 screens
├── 01_Leaf_Scanner_Home.png        <-- Screen 1 full render
├── 02_Diagnosis_Advisory.png       <-- Screen 2 full render
├── 03_Bilingual_Chatbot.png        <-- Screen 3 full render
├── 04_Coffee_Marketplace.png       <-- Screen 4 full render
├── 05_Create_Lot_Listing.png       <-- Screen 5 full render
├── 06_History_and_Profile.png      <-- Screen 6 full render
├── build_mobile_designs.py         <-- Parametric Python script driving figcraft-cli
└── README.md                       <-- This documentation file
```

---

## 5. How to View and Edit the Designs

### Option A: Import into Figma (Recommended)
1. Open [Figma](https://www.figma.com/) in your browser or desktop app.
2. In your Figma Workspace or Drafts, click the **Import** button (or drag and drop).
3. Select `plantiq_mobile_v2.fig` from this folder.
4. All frames, auto-layouts, vector shapes, colors, and text hierarchies will open natively in Figma.

### Option B: Inspect or Re-export with figcraft-cli
You can re-render any screen or export SVGs using `figcraft-cli`:
```bash
# Export individual screen as SVG
figcraft-cli export plantiq_mobile_redesign.figcraft -n "01_Leaf_Scanner_Home" -o screen1.svg --format svg

# Re-export canvas preview as PNG
figcraft-cli export plantiq_mobile_redesign.figcraft -o canvas.png --format png
```

### Option C: Re-run Parametric Generator
If you wish to alter color palettes, typography, or add extra screens:
```bash
python build_mobile_designs.py
```
