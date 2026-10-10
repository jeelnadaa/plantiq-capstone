import os
import subprocess
import base64

CHROME_PATH = r"C:\Users\solarquack\.cache\hyperframes\chrome\chrome-headless-shell\win64-152.0.7977.30\chrome-headless-shell-win64\chrome-headless-shell.exe"
WWW_DIR = r"d:\end-capstone-project\cleaned\mobile\www"
SNAP_DIR = os.path.join(WWW_DIR, "snapshots")
OUT_DIR = r"d:\end-capstone-project\cleaned\brag-output\composition\assets\images"
SAMPLE_IMG_DIR = r"d:\end-capstone-project\model-comparator\sample_images"

os.makedirs(SNAP_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# Load sample leaf images as base64
with open(os.path.join(SAMPLE_IMG_DIR, "rust_sample.jpg"), "rb") as f:
    rust_b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

with open(os.path.join(SAMPLE_IMG_DIR, "cercospora_sample.jpg"), "rb") as f:
    cercospora_b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

with open(os.path.join(SAMPLE_IMG_DIR, "healthy_sample.jpg"), "rb") as f:
    healthy_b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

HEAD_COMMON = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>PlantIQ</title>
  <link rel="stylesheet" href="../static/css/base.css?v=3.0">
  <link rel="stylesheet" href="../static/css/navbar.css?v=3.0">
  <link rel="stylesheet" href="../static/css/scanner.css?v=3.0">
  <link rel="stylesheet" href="../static/css/chat.css?v=3.0">
  <link rel="stylesheet" href="../static/css/marketplace.css?v=3.0">
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #fbf9f4 !important; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden; width: 412px; height: 892px; }
    .app-container { width: 412px; height: 892px; margin: 0 auto; display: flex; flex-direction: column; position: relative; overflow: hidden; background: #fbf9f4; }
    .page-content { flex: 1; overflow-y: hidden; padding: 12px 14px 68px 14px; display: flex; flex-direction: column; gap: 11px; height: 778px; }
  </style>
</head>
<body>
<div class="app-container">
  <header class="page-header" style="height: 52px; border-bottom: 2.5px solid #000000; padding: 8px 14px; display: flex; align-items: center; justify-content: space-between; background: #ffffff; flex-shrink: 0;">
    <div class="brand" style="display:flex; align-items:center; gap:8px;">
      <div class="brand-icon" style="width:32px; height:32px; background:#15803d; border:2px solid #000; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#fff;">
        <i data-lucide="leaf" style="width:18px; height:18px;"></i>
      </div>
      <span class="brand-name" style="font-weight:900; font-size:1.22rem; letter-spacing:-0.5px;">PlantIQ</span>
    </div>
    <div class="header-actions" style="display:flex; align-items:center; gap:8px;">
      <button class="btn-theme" style="position:relative; width:32px; height:32px; border:2px solid #000; border-radius:8px; background:#fff; display:flex; align-items:center; justify-content:center;">
        <i data-lucide="server" style="width:15px; height:15px;"></i>
        <span style="position:absolute; top:3px; right:3px; width:7px; height:7px; border-radius:50%; background:#22c55e; border:1px solid #000;"></span>
      </button>
      <button class="btn-theme" style="width:32px; height:32px; border:2px solid #000; border-radius:8px; background:#fff; display:flex; align-items:center; justify-content:center;">
        <i data-lucide="moon" style="width:15px; height:15px;"></i>
      </button>
      <div style="background:#e11d48; color:#fff; border:2px solid #000; font-weight:800; font-size:0.75rem; padding:4px 8px; border-radius:8px; display:flex; align-items:center; gap:4px; box-shadow:1.5px 1.5px 0px #000;">
        <i data-lucide="globe" style="width:13px; height:13px;"></i> EN
      </div>
    </div>
  </header>
'''

NAV_COMMON = lambda active_tab: f'''
  <nav class="bottom-tab-bar" style="position:absolute; bottom:0; left:0; width:100%; height:62px; border-top:2.5px solid #000; background:#fff; z-index:1000; display:flex; justify-content:space-around; align-items:center;">
    <div class="tab-item {'active' if active_tab=='scanner' else ''}" style="display:flex; flex-direction:column; align-items:center; gap:2px; font-size:0.7rem; font-weight:700; color:{'#15803d' if active_tab=='scanner' else '#4b5563'};">
      <i data-lucide="scan" style="width:20px; height:20px;"></i>
      <span>Scanner</span>
    </div>
    <div class="tab-item {'active' if active_tab=='chat' else ''}" style="display:flex; flex-direction:column; align-items:center; gap:2px; font-size:0.7rem; font-weight:700; color:{'#15803d' if active_tab=='chat' else '#4b5563'};">
      <i data-lucide="message-square" style="width:20px; height:20px;"></i>
      <span>Chat AI</span>
    </div>
    <div class="tab-item {'active' if active_tab=='market' else ''}" style="display:flex; flex-direction:column; align-items:center; gap:2px; font-size:0.7rem; font-weight:700; color:{'#15803d' if active_tab=='market' else '#4b5563'};">
      <i data-lucide="shopping-bag" style="width:20px; height:20px;"></i>
      <span>Market</span>
    </div>
    <div class="tab-item {'active' if active_tab=='history' else ''}" style="display:flex; flex-direction:column; align-items:center; gap:2px; font-size:0.7rem; font-weight:700; color:{'#15803d' if active_tab=='history' else '#4b5563'};">
      <i data-lucide="clock" style="width:20px; height:20px;"></i>
      <span>History</span>
    </div>
  </nav>
  <script>lucide.createIcons();</script>
</div>
</body>
</html>
'''

# -----------------------------------------------------------------------------
# 1. Screen 1: Scanner Home (Spacious, Large Text, Reaches Bottom)
# -----------------------------------------------------------------------------
html_s1 = HEAD_COMMON + f'''
  <main class="page-content">
    <div>
      <h1 style="font-size:1.25rem; font-weight:900; margin-bottom:2px;">Coffee Leaf Disease Diagnostic</h1>
      <p style="font-size:0.78rem; color:#4b5563; line-height:1.35;">Capture or upload coffee leaf photos to detect diseases and receive verified CCRI advisories.</p>
    </div>

    <!-- Prominent Camera Upload Dropzone -->
    <div style="border:2.5px dashed #000; border-radius:14px; background:#fff; padding:18px 14px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; box-shadow:3px 3px 0px #000; text-align:center;">
      <div style="width:54px; height:54px; border-radius:50%; background:#dcfce7; border:2px solid #000; display:flex; align-items:center; justify-content:center; color:#15803d;">
        <i data-lucide="camera" style="width:28px; height:28px;"></i>
      </div>
      <div>
        <strong style="font-size:1.02rem; display:block;">Tap to Take Photo or Upload Image</strong>
        <span style="font-size:0.75rem; color:#6b7280;">High-resolution Arabica / Robusta foliar sample</span>
      </div>
      <div style="display:flex; gap:8px; margin-top:2px;">
        <span style="background:#f3f4f6; border:1px solid #d1d5db; border-radius:6px; font-size:0.72rem; font-weight:700; padding:3px 8px;">Natural Sunlight</span>
        <span style="background:#f3f4f6; border:1px solid #d1d5db; border-radius:6px; font-size:0.72rem; font-weight:700; padding:3px 8px;">Single Leaf</span>
        <span style="background:#f3f4f6; border:1px solid #d1d5db; border-radius:6px; font-size:0.72rem; font-weight:700; padding:3px 8px;">Macro 1x-2x</span>
      </div>
      <div style="display:flex; gap:8px; width:100%; margin-top:4px;">
        <button style="flex:1; background:#f9fafb; border:1.5px solid #000; border-radius:8px; padding:6px; font-size:0.76rem; font-weight:800; display:flex; align-items:center; justify-content:center; gap:5px;">
          <i data-lucide="camera" style="width:14px; height:14px;"></i> Open Camera
        </button>
        <button style="flex:1; background:#f9fafb; border:1.5px solid #000; border-radius:8px; padding:6px; font-size:0.76rem; font-weight:800; display:flex; align-items:center; justify-content:center; gap:5px;">
          <i data-lucide="image" style="width:14px; height:14px;"></i> Upload Gallery
        </button>
      </div>
    </div>

    <!-- Active GPS Telemetry Card -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:9px 12px; display:flex; justify-content:space-between; align-items:center; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; align-items:center; gap:8px;">
        <i data-lucide="map-pin" style="width:18px; height:18px; color:#15803d;"></i>
        <div>
          <strong style="font-size:0.82rem; display:block;">Location & Microclimate</strong>
          <span style="font-size:0.76rem; color:#15803d; font-weight:700;">Chikkamagaluru (13.3161°N, 75.7720°E) • 980m</span>
        </div>
      </div>
      <span style="background:#dcfce7; color:#15803d; border:1.5px solid #15803d; font-size:0.72rem; font-weight:800; padding:3px 8px; border-radius:6px;">GPS Active</span>
    </div>

    <!-- Optional Question Input -->
    <div style="display:flex; gap:8px;">
      <input type="text" placeholder="Optional question (e.g. spray schedule)" style="flex:1; border:2px solid #000; border-radius:10px; padding:9px 12px; font-size:0.8rem; background:#fff; box-shadow:2px 2px 0px #000; outline:none;" readonly value="">
      <button style="width:40px; height:40px; border:2px solid #000; border-radius:10px; background:#fff; display:flex; align-items:center; justify-content:center; box-shadow:2px 2px 0px #000; color:#15803d;">
        <i data-lucide="mic" style="width:18px; height:18px;"></i>
      </button>
    </div>

    <!-- Analyze Button -->
    <button style="width:100%; background:#2d5bff; color:#fff; border:2.5px solid #000; border-radius:12px; padding:11px; font-weight:900; font-size:0.94rem; box-shadow:3px 3px 0px #000; display:flex; align-items:center; justify-content:center; gap:8px;">
      <i data-lucide="sparkles" style="width:18px; height:18px;"></i>
      Analyze Leaf with ResNet-50
    </button>

    <!-- Recent Diagnostic Scans Strip -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:9px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <strong style="font-size:0.82rem; color:#111827;">Recent Diagnostic Scans</strong>
        <span style="font-size:0.74rem; color:#15803d; font-weight:800;">View History →</span>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        <div style="display:flex; align-items:center; gap:8px; background:#f9fafb; border:1px solid #e5e7eb; padding:6px 8px; border-radius:8px;">
          <img src="{rust_b64}" style="width:30px; height:30px; border-radius:6px; object-fit:cover; border:1px solid #000;">
          <div><strong style="font-size:0.8rem; display:block;">Leaf Rust</strong><span style="font-size:0.72rem; color:#15803d; font-weight:700;">96.4% • Today</span></div>
        </div>
        <div style="display:flex; align-items:center; gap:8px; background:#f9fafb; border:1px solid #e5e7eb; padding:6px 8px; border-radius:8px;">
          <img src="{healthy_b64}" style="width:30px; height:30px; border-radius:6px; object-fit:cover; border:1px solid #000;">
          <div><strong style="font-size:0.8rem; display:block;">Healthy</strong><span style="font-size:0.72rem; color:#15803d; font-weight:700;">98.7% • 03 Oct</span></div>
        </div>
      </div>
    </div>

    <!-- CCRI Diagnostic Models & Grounding Card (Reaches tab bar) -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:9px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <strong style="font-size:0.82rem; color:#111827;">Model Status: PyTorch ResNet-50</strong>
        <span style="font-size:0.72rem; color:#15803d; font-weight:800; background:#dcfce7; border:1px solid #15803d; padding:2px 6px; border-radius:5px;">20ms • 96.4% Acc</span>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.76rem; color:#374151; margin-bottom:6px;">
        <div style="background:#f9fafb; border:1px solid #e5e7eb; padding:5px 8px; border-radius:6px;">☕ Leaf Rust (96.4%)</div>
        <div style="background:#f9fafb; border:1px solid #e5e7eb; padding:5px 8px; border-radius:6px;">🍂 Cercospora Spot</div>
        <div style="background:#f9fafb; border:1px solid #e5e7eb; padding:5px 8px; border-radius:6px;">🐛 Coffee Leaf Miner</div>
        <div style="background:#f9fafb; border:1px solid #e5e7eb; padding:5px 8px; border-radius:6px;">🌿 Healthy Control</div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#6b7280; border-top:1px dashed #d1d5db; padding-top:5px;">
        <span>Central Coffee Research Institute Manuals</span>
        <span style="font-weight:700; color:#15803d;">✓ 14 Guides Attached</span>
      </div>
    </div>
  </main>
''' + NAV_COMMON('scanner')

# -----------------------------------------------------------------------------
# 2. Screen 2: Leaf Uploaded (Analyzing State - Spacious, Large Text)
# -----------------------------------------------------------------------------
html_s2 = HEAD_COMMON + f'''
  <main class="page-content">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 style="font-size:1.22rem; font-weight:900; margin-bottom:2px;">Leaf Scan in Progress</h1>
        <p style="font-size:0.78rem; color:#4b5563;">Classifying disease & querying CCRI knowledge base...</p>
      </div>
      <span style="background:#fef3c7; color:#92400e; border:1.5px solid #d97706; font-size:0.74rem; font-weight:800; padding:3px 9px; border-radius:6px;">Processing</span>
    </div>

    <!-- Prominent Leaf Image Preview with Live Scan Reticle -->
    <div style="border:2.5px solid #000; border-radius:14px; overflow:hidden; background:#000; position:relative; box-shadow:3px 3px 0px #000; height:310px;">
      <img src="{rust_b64}" style="width:100%; height:100%; object-fit:cover; display:block; opacity:0.92;">
      <!-- Bounding Box / Scan Reticle -->
      <div style="position:absolute; top:45px; left:55px; width:210px; height:185px; border:2.5px dashed #22c55e; border-radius:8px; box-shadow:0 0 16px rgba(34,197,94,0.6); pointer-events:none;">
        <span style="position:absolute; top:-12px; left:8px; background:#15803d; color:#fff; font-size:0.7rem; font-weight:800; padding:2px 8px; border-radius:5px; border:1px solid #000;">Lesion Detected</span>
      </div>
      <!-- Geotag Badge Overlay -->
      <div style="position:absolute; bottom:10px; left:10px; right:10px; background:rgba(0,0,0,0.82); border:1.5px solid #fff; border-radius:8px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center; color:#fff; font-size:0.75rem;">
        <span style="display:flex; align-items:center; gap:5px;"><i data-lucide="map-pin" style="width:14px; height:14px; color:#22c55e;"></i> Chikkamagaluru (980m)</span>
        <span style="font-weight:700; color:#4ade80;">78% RH Locked</span>
      </div>
    </div>

    <!-- Active 4-Stage Inference & RAG Pipeline Checklist -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:11px 14px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <strong style="font-size:0.84rem; color:#111827;">Diagnostic Pipeline Progress</strong>
        <span style="font-size:0.75rem; color:#15803d; font-weight:800;">75% Complete</span>
      </div>
      <div style="height:7px; background:#e5e7eb; border-radius:999px; overflow:hidden; border:1.5px solid #000; margin-bottom:9px;">
        <div style="width:75%; height:100%; background:#15803d;"></div>
      </div>
      <div style="display:flex; flex-direction:column; gap:6px; font-size:0.78rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; color:#15803d; font-weight:700;">
          <span style="display:flex; align-items:center; gap:6px;"><i data-lucide="check-circle-2" style="width:15px; height:15px;"></i> 1. CNN Feature Extraction (ResNet-50)</span>
          <span style="font-size:0.72rem; color:#6b7280;">18ms</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; color:#15803d; font-weight:700;">
          <span style="display:flex; align-items:center; gap:6px;"><i data-lucide="check-circle-2" style="width:15px; height:15px;"></i> 2. Hybrid RAG Match (BM25 + BGE)</span>
          <span style="font-size:0.72rem; color:#6b7280;">32ms</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; color:#2563eb; font-weight:700;">
          <span style="display:flex; align-items:center; gap:6px;"><i data-lucide="loader-2" style="width:15px; height:15px;"></i> 3. Microclimate Agronomic Synthesis</span>
          <span style="font-size:0.72rem; color:#2563eb;">Active</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; color:#9ca3af; font-weight:600;">
          <span style="display:flex; align-items:center; gap:6px;"><i data-lucide="circle" style="width:15px; height:15px;"></i> 4. Bilingual Translation (Kannada / English)</span>
          <span style="font-size:0.72rem; color:#9ca3af;">Queued</span>
        </div>
      </div>
    </div>

    <!-- Estate & Canopy Context -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:9px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; justify-content:space-between; align-items:center; font-size:0.78rem;">
      <div>
        <strong style="display:block; color:#111827;">Canopy: 60% Diffused Shade</strong>
        <span style="color:#6b7280; font-size:0.74rem;">Silver Oak & Dadap Shade Cover</span>
      </div>
      <div style="text-align:right;">
        <strong style="display:block; color:#b91c1c;">Spore Risk: High</strong>
        <span style="color:#6b7280; font-size:0.74rem;">Humidity > 75%</span>
      </div>
    </div>

    <!-- Live Telemetry Card (Reaches tab bar) -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:9px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; justify-content:space-between; align-items:center; font-size:0.76rem;">
      <span style="color:#374151;"><strong>Telemetry:</strong> 24.5°C • Wind 6 km/h SW • Chikkamagaluru</span>
      <span style="color:#15803d; font-weight:800;">Optimal Scan</span>
    </div>
  </main>
''' + NAV_COMMON('scanner')

# -----------------------------------------------------------------------------
# 3. Screen 3: ResNet-50 Classification Diagnosis (Spacious, Large Text)
# -----------------------------------------------------------------------------
html_s3 = HEAD_COMMON + f'''
  <main class="page-content">
    <!-- Leaf Preview Strip -->
    <div style="display:flex; align-items:center; justify-content:space-between; border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{rust_b64}" style="width:38px; height:38px; object-fit:cover; border-radius:8px; border:1.5px solid #000;">
        <div>
          <div style="font-weight:900; font-size:0.86rem;">Input Leaf Image Processed</div>
          <div style="font-size:0.74rem; color:#6b7280;">PyTorch ResNet-50 • 20ms Local Inference</div>
        </div>
      </div>
      <span style="background:#fee2e2; color:#b91c1c; border:1.5px solid #b91c1c; font-weight:800; font-size:0.74rem; padding:3px 9px; border-radius:999px;">Detected</span>
    </div>

    <!-- Main Diagnosis Card -->
    <div style="border:2px solid #000; border-radius:14px; background:#fff; padding:12px 14px; box-shadow:3px 3px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px;">
        <div>
          <h2 style="font-size:1.32rem; font-weight:900; margin:0;">Coffee Leaf Rust</h2>
          <div style="font-size:0.76rem; color:#4b5563; font-style:italic;">Hemileia vastatrix • Urediniospore Foliar Infection</div>
        </div>
        <span style="font-size:1.45rem; font-weight:900; color:#15803d;">96.4%</span>
      </div>

      <!-- Confidence Bar -->
      <div style="height:8px; background:#e5e7eb; border-radius:999px; overflow:hidden; border:1.5px solid #000; margin:6px 0 9px 0;">
        <div style="width:96.4%; height:100%; background:#15803d;"></div>
      </div>

      <!-- Class Probabilities Grid -->
      <strong style="font-size:0.78rem; color:#374151; display:block; margin-bottom:5px;">ResNet-50 Class Probabilities</strong>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:9px; font-size:0.76rem;">
        <div style="background:#f0fdf4; border:1.5px solid #15803d; padding:5px 8px; border-radius:6px; display:flex; justify-content:space-between;"><span>Rust</span><strong style="color:#15803d;">96.4%</strong></div>
        <div style="background:#f9fafb; border:1px solid #d1d5db; padding:5px 8px; border-radius:6px; display:flex; justify-content:space-between;"><span>Cercospora</span><strong>2.1%</strong></div>
        <div style="background:#f9fafb; border:1px solid #d1d5db; padding:5px 8px; border-radius:6px; display:flex; justify-content:space-between;"><span>Phoma</span><strong>0.8%</strong></div>
        <div style="background:#f9fafb; border:1px solid #d1d5db; padding:5px 8px; border-radius:6px; display:flex; justify-content:space-between;"><span>Leaf Miner</span><strong>0.5%</strong></div>
      </div>

      <button style="width:100%; background:#2d5bff; color:#fff; border:2px solid #000; border-radius:10px; padding:8px; font-weight:800; font-size:0.84rem; box-shadow:2px 2px 0px #000; display:flex; align-items:center; justify-content:center; gap:6px;">
        <i data-lucide="message-square" style="width:15px; height:15px;"></i> Ask AI Follow-Up in Chat
      </button>
    </div>

    <!-- Recommended Field Action Card -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:11px 14px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
        <strong style="font-size:0.82rem; color:#b91c1c; display:flex; align-items:center; gap:5px;">
          <i data-lucide="alert-triangle" style="width:15px; height:15px;"></i> Recommended Field Action
        </strong>
        <span style="font-size:0.72rem; background:#fee2e2; color:#b91c1c; border:1px solid #b91c1c; font-weight:800; padding:2px 6px; border-radius:5px;">High Priority</span>
      </div>
      <p style="font-size:0.78rem; color:#1f2937; line-height:1.4; margin-bottom:8px;">
        Apply <strong>Bordeaux mixture 1%</strong> protective foliar spray within 48 hours to arrest fungal spore germination under 78% relative humidity.
      </p>
      <div style="display:flex; gap:8px;">
        <button style="flex:1; background:#15803d; color:#fff; border:1.5px solid #000; padding:7px; border-radius:8px; font-weight:800; font-size:0.76rem; display:flex; align-items:center; justify-content:center; gap:4px;">
          <i data-lucide="file-text" style="width:14px; height:14px;"></i> View Full Advisory
        </button>
        <button style="flex:1; background:#fff; color:#000; border:1.5px solid #000; padding:7px; border-radius:8px; font-weight:800; font-size:0.76rem; display:flex; align-items:center; justify-content:center; gap:4px;">
          <i data-lucide="bookmark" style="width:14px; height:14px;"></i> Save to History
        </button>
      </div>
    </div>

    <!-- Microclimate Spore Risk Card -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:10px 14px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <strong style="font-size:0.8rem; color:#111827;">Microclimate Spore Germination Index</strong>
        <span style="font-size:0.72rem; color:#b91c1c; font-weight:800;">78% RH • High Risk</span>
      </div>
      <div style="font-size:0.76rem; color:#4b5563; line-height:1.35; margin-bottom:5px;">
        Current conditions in Chikkamagaluru (980m) favor rapid pustule dispersal. Complete spray before next forecasted rainfall.
      </div>
      <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#6b7280; border-top:1px dashed #d1d5db; padding-top:4px;">
        <span>Pathology: Abaxial powdery pustules</span>
        <span style="color:#15803d; font-weight:700;">Defoliation Risk: Moderate</span>
      </div>
    </div>

    <!-- Yield Protection Advisory Card (Reaches tab bar) -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:9px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; justify-content:space-between; align-items:center; font-size:0.76rem;">
      <div>
        <strong style="display:block; color:#111827;">Yield Protection Advisory</strong>
        <span style="color:#6b7280; font-size:0.72rem;">Prompt treatment prevents 30-40% foliar drop</span>
      </div>
      <span style="background:#dcfce7; color:#15803d; border:1px solid #15803d; padding:3px 8px; border-radius:6px; font-weight:800; font-size:0.72rem;">Score: 0.968</span>
    </div>
  </main>
''' + NAV_COMMON('scanner')

# -----------------------------------------------------------------------------
# 4. Screen 4: CCRI Treatment Advisory (Spacious, Large Text, Fully Filled)
# -----------------------------------------------------------------------------
html_s4 = HEAD_COMMON + f'''
  <main class="page-content">
    <!-- Disease Context Strip -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; justify-content:space-between; align-items:center;">
      <div style="display:flex; align-items:center; gap:8px;">
        <img src="{rust_b64}" style="width:32px; height:32px; border-radius:6px; object-fit:cover; border:1.5px solid #000;">
        <span style="font-weight:900; font-size:0.86rem;">Coffee Leaf Rust (96.4%)</span>
      </div>
      <span style="font-size:0.74rem; color:#15803d; font-weight:800; background:#dcfce7; border:1px solid #15803d; padding:3px 8px; border-radius:6px;">Chikkamagaluru 980m</span>
    </div>

    <!-- Main Advisory Card (Full CCRI Protocols) -->
    <div style="border:2px solid #000; border-radius:14px; background:#fff; padding:12px 14px; box-shadow:3px 3px 0px #000;">
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; border-bottom:1.5px solid #f3f4f6; padding-bottom:6px;">
        <div style="width:32px; height:32px; background:#dcfce7; border-radius:8px; border:2px solid #000; display:flex; align-items:center; justify-content:center; color:#15803d;">
          <i data-lucide="shield-check" style="width:18px; height:18px;"></i>
        </div>
        <div>
          <div style="font-size:0.95rem; font-weight:900;">CCRI Treatment Advisory</div>
          <div style="font-size:0.72rem; color:#6b7280;">Hybrid RAG: BGE-Base + BM25 + Cross-Encoder</div>
        </div>
      </div>

      <!-- 1. Chemical Spray Protocol -->
      <div style="background:#f0fdf4; border:1.5px solid #16a34a; border-left:4px solid #16a34a; padding:7px 10px; border-radius:8px; margin-bottom:7px;">
        <strong style="display:block; font-size:0.8rem; color:#166534; margin-bottom:2px;">1. Chemical Spray Formulations</strong>
        <p style="font-size:0.76rem; color:#1f2937; margin:0; line-height:1.4;">
          • <strong>Pre-Monsoon (May–June)</strong>: Foliar spray of <strong>Bordeaux mixture 1%</strong> (1 kg copper sulphate + 1 kg quicklime in 100 L water).<br>
          • <strong>Post-Monsoon (Sept–Oct)</strong>: Systemic spray of <strong>Bayleton 25 WP</strong> (160 g / 200 L barrel) or <strong>Contaf 5% EC</strong> (300 ml / barrel).
        </p>
      </div>

      <!-- 2. Cultural Management Protocol -->
      <div style="background:#eff6ff; border:1.5px solid #2563eb; border-left:4px solid #2563eb; padding:7px 10px; border-radius:8px; margin-bottom:7px;">
        <strong style="display:block; font-size:0.8rem; color:#1e40af; margin-bottom:2px;">2. Cultural & Shade Regulation</strong>
        <p style="font-size:0.76rem; color:#1f2937; margin:0; line-height:1.4;">
          • Thin Dadap and Silver Oak shade trees to guarantee <strong>50–60% diffused sunlight</strong>, reducing leaf dampness hours.
        </p>
      </div>

      <!-- 3. Organic Biocontrol & Spray Technique -->
      <div style="background:#fefce8; border:1.5px solid #ca8a04; border-left:4px solid #ca8a04; padding:7px 10px; border-radius:8px; margin-bottom:7px;">
        <strong style="display:block; font-size:0.8rem; color:#854d0e; margin-bottom:2px;">3. Organic Biocontrol & Spray Technique</strong>
        <p style="font-size:0.76rem; color:#1f2937; margin:0; line-height:1.4;">
          • Use hollow-cone nozzle directed upwards to coat underside of canopy foliage where rust spores germinate.
        </p>
      </div>

      <!-- Grounding Footer -->
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.72rem; color:#4b5563; border-top:1px solid #f3f4f6; padding-top:5px;">
        <span>CCRI Coffee Agronomy Manual</span>
        <span style="background:#e5e7eb; border:1px solid #000; padding:2px 8px; border-radius:999px; font-weight:800;">Score: 0.968</span>
      </div>
    </div>

    <!-- Microclimate Spray Timing Card -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:10px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <strong style="font-size:0.82rem; color:#111827; display:flex; align-items:center; gap:5px;">
          <i data-lucide="clock" style="width:15px; height:15px; color:#15803d;"></i> Microclimate Spraying Window (GPS)
        </strong>
        <span style="font-size:0.72rem; background:#dcfce7; color:#15803d; border:1px solid #15803d; font-weight:800; padding:2px 7px; border-radius:5px;">78% RH Locked</span>
      </div>
      <p style="font-size:0.76rem; color:#374151; line-height:1.4; margin-bottom:8px;">
        <strong>Optimal Spraying:</strong> 06:30 AM – 09:30 AM before afternoon thermal evaporation. Spray lower leaf surfaces thoroughly where fungal pustules reside.
      </p>
      <div style="display:flex; gap:8px;">
        <button style="flex:1; background:#e11d48; color:#fff; border:1.5px solid #000; padding:8px; border-radius:8px; font-weight:800; font-size:0.76rem; display:flex; align-items:center; justify-content:center; gap:4px; box-shadow:1.5px 1.5px 0px #000;">
          <i data-lucide="volume-2" style="width:14px; height:14px;"></i> ಧ್ವನಿ (Listen in Kannada)
        </button>
        <button style="flex:1; background:#2d5bff; color:#fff; border:1.5px solid #000; padding:8px; border-radius:8px; font-weight:800; font-size:0.76rem; display:flex; align-items:center; justify-content:center; gap:4px; box-shadow:1.5px 1.5px 0px #000;">
          <i data-lucide="message-square" style="width:14px; height:14px;"></i> Ask AI Follow-Up
        </button>
      </div>
    </div>

    <!-- Official Advisory Grounding Strip (Reaches tab bar) -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; justify-content:space-between; align-items:center; font-size:0.74rem;">
      <div style="display:flex; align-items:center; gap:6px;">
        <i data-lucide="check-circle" style="width:15px; height:15px; color:#15803d;"></i>
        <span style="font-weight:700; color:#111827;">Central Coffee Research Institute, Balehonnur</span>
      </div>
      <span style="color:#6b7280; font-weight:600;">Manual #04</span>
    </div>
  </main>
''' + NAV_COMMON('scanner')

# -----------------------------------------------------------------------------
# 5. Screen 5: Microclimate Telemetry (Spacious, Large Text, Beautifully Filled)
# -----------------------------------------------------------------------------
html_s5 = HEAD_COMMON.replace('gap: 11px;', 'gap: 9px;') + f'''
  <main class="page-content" style="gap: 8px; padding: 10px 14px 68px 14px;">
    <!-- Header Card -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:8px;">
          <div style="width:32px; height:32px; background:#dcfce7; border:1.5px solid #000; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#15803d;">
            <i data-lucide="map-pin" style="width:18px; height:18px;"></i>
          </div>
          <div>
            <div style="font-size:0.92rem; font-weight:900;">Estate Microclimate Telemetry</div>
            <div style="font-size:0.75rem; color:#15803d; font-weight:700;">Chikkamagaluru (13.3161°N, 75.7720°E)</div>
          </div>
        </div>
        <span style="background:#f3f4f6; border:1px solid #000; font-size:0.72rem; font-weight:800; padding:3px 8px; border-radius:6px;">Live Open-Meteo</span>
      </div>
    </div>

    <!-- 4 Environmental Metrics Grid -->
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:7px;">
      <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
        <span style="font-size:0.75rem; color:#6b7280; font-weight:700;">Elevation</span>
        <div style="font-size:1.42rem; font-weight:900; color:#111827; margin:1px 0;">980 m</div>
        <span style="font-size:0.72rem; color:#15803d; font-weight:800;">Highland Arabica</span>
      </div>

      <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
        <span style="font-size:0.75rem; color:#6b7280; font-weight:700;">Temperature</span>
        <div style="font-size:1.42rem; font-weight:900; color:#111827; margin:1px 0;">24.5 °C</div>
        <span style="font-size:0.72rem; color:#6b7280; font-weight:700;">Feels 25.0°C</span>
      </div>

      <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; border-color:#b91c1c;">
        <span style="font-size:0.75rem; color:#b91c1c; font-weight:800;">Relative Humidity</span>
        <div style="font-size:1.42rem; font-weight:900; color:#b91c1c; margin:1px 0;">78.0 %</div>
        <span style="font-size:0.72rem; color:#b91c1c; font-weight:800;">High spore risk</span>
      </div>

      <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
        <span style="font-size:0.75rem; color:#6b7280; font-weight:700;">Soil pH (Estimated)</span>
        <div style="font-size:1.42rem; font-weight:900; color:#111827; margin:1px 0;">6.2 pH</div>
        <span style="font-size:0.72rem; color:#15803d; font-weight:800;">Optimal zone</span>
      </div>
    </div>

    <!-- Hourly Foliar Spray Suitability Window -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
        <strong style="font-size:0.82rem; color:#111827;">Today's Spray Suitability Timeline</strong>
        <span style="font-size:0.72rem; color:#15803d; font-weight:800;">Best: Morning</span>
      </div>
      <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:5px; text-align:center;">
        <div style="background:#dcfce7; border:1px solid #15803d; border-radius:7px; padding:3px 2px;">
          <div style="font-size:0.7rem; color:#6b7280; font-weight:700;">06:30</div>
          <strong style="font-size:0.76rem; color:#15803d; display:block;">IDEAL</strong>
          <span style="font-size:0.66rem; color:#15803d;">78% RH</span>
        </div>
        <div style="background:#dcfce7; border:1px solid #15803d; border-radius:7px; padding:3px 2px;">
          <div style="font-size:0.7rem; color:#6b7280; font-weight:700;">08:30</div>
          <strong style="font-size:0.76rem; color:#15803d; display:block;">IDEAL</strong>
          <span style="font-size:0.66rem; color:#15803d;">74% RH</span>
        </div>
        <div style="background:#fef3c7; border:1px solid #d97706; border-radius:7px; padding:3px 2px;">
          <div style="font-size:0.7rem; color:#6b7280; font-weight:700;">11:30</div>
          <strong style="font-size:0.76rem; color:#d97706; display:block;">MOD</strong>
          <span style="font-size:0.66rem; color:#d97706;">62% RH</span>
        </div>
        <div style="background:#fee2e2; border:1px solid #b91c1c; border-radius:7px; padding:3px 2px;">
          <div style="font-size:0.7rem; color:#6b7280; font-weight:700;">14:00</div>
          <strong style="font-size:0.76rem; color:#b91c1c; display:block;">AVOID</strong>
          <span style="font-size:0.66rem; color:#b91c1c;">Hot sun</span>
        </div>
        <div style="background:#fef3c7; border:1px solid #d97706; border-radius:7px; padding:3px 2px;">
          <div style="font-size:0.7rem; color:#6b7280; font-weight:700;">17:00</div>
          <strong style="font-size:0.76rem; color:#d97706; display:block;">FAIR</strong>
          <span style="font-size:0.66rem; color:#d97706;">Evening</span>
        </div>
      </div>
    </div>

    <!-- Agronomic Rule Trigger Banner -->
    <div style="background:#fefce8; border:2px solid #000; border-radius:12px; padding:7px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="font-size:0.78rem; color:#854d0e; line-height:1.35;">
        <strong>🌧 Agronomic Adaptation:</strong> High humidity (78%) in Chikkamagaluru triggers recommendation for pre-monsoon protective spray before rainfall onset.
      </div>
    </div>

    <!-- 7-Day Foliar Spore Pressure Forecast -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
        <strong style="font-size:0.82rem; color:#111827;">7-Day Foliar Spore Pressure Forecast</strong>
        <span style="font-size:0.72rem; color:#b91c1c; font-weight:800;">Next Rain: 36h (12mm)</span>
      </div>
      <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:5px; text-align:center;">
        <div style="background:#fee2e2; border:1px solid #b91c1c; border-radius:7px; padding:4px 2px;">
          <div style="font-size:0.72rem; color:#6b7280; font-weight:700;">Mon</div>
          <strong style="font-size:0.88rem; color:#b91c1c; display:block;">78%</strong>
          <span style="font-size:0.68rem; color:#b91c1c; font-weight:800;">HIGH</span>
        </div>
        <div style="background:#fee2e2; border:1px solid #b91c1c; border-radius:7px; padding:4px 2px;">
          <div style="font-size:0.72rem; color:#6b7280; font-weight:700;">Tue</div>
          <strong style="font-size:0.88rem; color:#b91c1c; display:block;">82%</strong>
          <span style="font-size:0.68rem; color:#b91c1c; font-weight:800;">HIGH</span>
        </div>
        <div style="background:#fee2e2; border:1px solid #b91c1c; border-radius:7px; padding:4px 2px;">
          <div style="font-size:0.72rem; color:#6b7280; font-weight:700;">Wed</div>
          <strong style="font-size:0.88rem; color:#b91c1c; display:block;">80%</strong>
          <span style="font-size:0.68rem; color:#b91c1c; font-weight:800;">HIGH</span>
        </div>
        <div style="background:#fef3c7; border:1px solid #d97706; border-radius:7px; padding:4px 2px;">
          <div style="font-size:0.72rem; color:#6b7280; font-weight:700;">Thu</div>
          <strong style="font-size:0.88rem; color:#d97706; display:block;">65%</strong>
          <span style="font-size:0.68rem; color:#d97706; font-weight:800;">MOD</span>
        </div>
        <div style="background:#dcfce7; border:1px solid #15803d; border-radius:7px; padding:4px 2px;">
          <div style="font-size:0.72rem; color:#6b7280; font-weight:700;">Fri</div>
          <strong style="font-size:0.88rem; color:#15803d; display:block;">52%</strong>
          <span style="font-size:0.68rem; color:#15803d; font-weight:800;">LOW</span>
        </div>
      </div>
    </div>

    <!-- Planter Guidance & Hourly Window (Reaches tab bar with clean margin) -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000;">
      <strong style="font-size:0.82rem; color:#111827; display:block; margin-bottom:3px;">Planter Guidance Summary</strong>
      <div style="font-size:0.76rem; color:#374151; line-height:1.4;">
        • <strong>Spray Window:</strong> Tuesday morning (06:30 - 09:30 AM) before rainfall onset.<br>
        • <strong>Canopy Shade:</strong> Maintain 50-60% shade cover to accelerate morning leaf drying.
      </div>
    </div>
  </main>
''' + NAV_COMMON('scanner')

# -----------------------------------------------------------------------------
# 6. Screen 6: Bilingual Chatbot (Kannada / English - Spacious, Large Text)
# -----------------------------------------------------------------------------
html_s6 = HEAD_COMMON + f'''
  <main class="page-content" style="gap: 8px;">
    <!-- Context Ribbon -->
    <div style="border:2px solid #000; border-radius:10px; background:#fff; padding:7px 12px; box-shadow:2px 2px 0px #000; display:flex; justify-content:space-between; align-items:center; font-size:0.78rem;">
      <span style="font-weight:700; color:#111827;">📍 Chikkamagaluru (Active GPS)</span>
      <span style="background:#dcfce7; color:#15803d; border:1px solid #15803d; font-weight:800; padding:2px 6px; border-radius:5px; font-size:0.72rem;">Persistent Memory</span>
    </div>

    <!-- Leaf Scan Context Pill -->
    <div style="display:flex; align-items:center; gap:8px; background:#eff6ff; border:1.5px solid #2563eb; border-radius:10px; padding:6px 10px; font-size:0.78rem; color:#1e40af;">
      <img src="{rust_b64}" style="width:24px; height:24px; border-radius:5px; object-fit:cover; border:1px solid #000;">
      <span style="font-weight:700;">Context: Coffee Leaf Rust (96.4%) • 980m elevation</span>
    </div>

    <!-- Multi-Turn Bilingual Chat Messages -->
    <!-- Farmer Kannada Message 1 -->
    <div style="align-self:flex-end; max-width:85%; background:#15803d; color:#fff; border:2px solid #000; border-radius:14px 14px 2px 14px; padding:8px 12px; box-shadow:2px 2px 0px #000; font-size:0.84rem; line-height:1.4;">
      <div>ಎಲೆಗಳ ಮೇಲೆ ಹಳದಿ ಚುಕ್ಕೆಗಳಿವೆ, ಯಾವ ಔಷಧ ಸಿಂಪಡಿಸಬೇಕು?</div>
      <div style="text-align:right; font-size:0.68rem; color:#bbf7d0; margin-top:3px;">10:14 AM • Voice Input</div>
    </div>

    <!-- PlantIQ Response 1 -->
    <div style="align-self:flex-start; max-width:92%; background:#fff; color:#111827; border:2px solid #000; border-radius:14px 14px 14px 2px; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; font-size:0.82rem; line-height:1.4;">
      <strong style="color:#15803d; display:block; margin-bottom:3px; font-size:0.84rem;">PlantIQ ಕೃಷಿ ಸಲಹೆಗಾರ:</strong>
      ಇದು ಕಾಫಿ ಎಲೆ ತುಕ್ಕು (Coffee Leaf Rust) ರೋಗ. ಚಿಕ್ಕಮಗಳೂರಿನಲ್ಲಿ 78% ತೇವಾಂಶವಿರುವುದರಿಂದ:<br>
      <strong>1. ಬೋರ್ಡೋ ದ್ರಾವಣ 1%</strong> ಸಿಂಪಡಿಸಿ (1 ಕೆಜಿ ಮೈಲುತುತ್ತ + 1 ಕೆಜಿ ಸುಣ್ಣ / 100 ಲೀ ನೀರು).<br>
      <strong>2. ಮುಂಗಾರು ನಂತರ ಬೇಲಿಟಾನ್ 25 WP</strong> (160 ಗ್ರಾಂ / ಬ್ಯಾರೆಲ್) ಬಳಸಿ.
    </div>

    <!-- Farmer Follow-up 2 -->
    <div style="align-self:flex-end; max-width:82%; background:#15803d; color:#fff; border:2px solid #000; border-radius:14px 14px 2px 14px; padding:7px 12px; box-shadow:2px 2px 0px #000; font-size:0.84rem; line-height:1.4;">
      <div>ಸಿಂಪಡಿಸಲು ಸರಿಯಾದ ಸಮಯ ಯಾವುದು?</div>
      <div style="text-align:right; font-size:0.68rem; color:#bbf7d0; margin-top:2px;">10:16 AM • Audio</div>
    </div>

    <!-- PlantIQ Response 2 -->
    <div style="align-self:flex-start; max-width:90%; background:#fff; color:#111827; border:2px solid #000; border-radius:14px 14px 14px 2px; padding:7px 12px; box-shadow:2.5px 2.5px 0px #000; font-size:0.82rem; line-height:1.4;">
      ಬೆಳಿಗ್ಗೆ 6:30 ರಿಂದ 9:30 ರೊಳಗೆ ಸಿಂಪಡಿಸಿ. ತಾಪಮಾನ ಹೆಚ್ಚಾಗುವ ಮುನ್ನ ಎಲೆಗಳು ಔಷಧಿಯನ್ನು ಹೀರಿಕೊಳ್ಳುತ್ತವೆ.
    </div>

    <!-- Farmer Follow-up 3 -->
    <div style="align-self:flex-end; max-width:85%; background:#15803d; color:#fff; border:2px solid #000; border-radius:14px 14px 2px 14px; padding:7px 12px; box-shadow:2px 2px 0px #000; font-size:0.84rem; line-height:1.4;">
      <div>ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಕಾಫಿ ಬೆಲೆ ಎಷ್ಟಿದೆ? ನೇರವಾಗಿ ಮಾರಾಟ ಮಾಡಬಹುದೇ?</div>
      <div style="text-align:right; font-size:0.68rem; color:#bbf7d0; margin-top:2px;">10:17 AM • Text</div>
    </div>

    <!-- PlantIQ Response 3 -->
    <div style="align-self:flex-start; max-width:92%; background:#fff; color:#111827; border:2px solid #000; border-radius:14px 14px 14px 2px; padding:7px 12px; box-shadow:2.5px 2.5px 0px #000; font-size:0.82rem; line-height:1.4;">
      ಅರೇಬಿಕಾ ಪಾರ್ಚ್‌ಮೆಂಟ್ ಬೆಲೆ ₹14,800/50kg ಇದೆ. 'Market' ಟ್ಯಾಬ್‌ನಲ್ಲಿ ನಿಮ್ಮ ಬೆಳೆಯನ್ನು ನೇರವಾಗಿ ಖರೀದಿದಾರರಿಗೆ 0% ಕಮಿಷನ್‌ನಲ್ಲಿ ಪಟ್ಟಿ ಮಾಡಿ.
    </div>

    <!-- Quick Suggestion Pills -->
    <div style="display:flex; gap:6px; overflow-x:hidden; padding:2px 0;">
      <span style="background:#fff; border:1.5px solid #000; border-radius:999px; padding:4px 10px; font-size:0.75rem; font-weight:800; box-shadow:1.5px 1.5px 0px #000; white-space:nowrap;">ಬೋರ್ಡೋ ಪ್ರಮಾಣ?</span>
      <span style="background:#fff; border:1.5px solid #000; border-radius:999px; padding:4px 10px; font-size:0.75rem; font-weight:800; box-shadow:1.5px 1.5px 0px #000; white-space:nowrap;">Rainfall risk?</span>
      <span style="background:#fff; border:1.5px solid #000; border-radius:999px; padding:4px 10px; font-size:0.75rem; font-weight:800; box-shadow:1.5px 1.5px 0px #000; white-space:nowrap;">Sell Arabica</span>
    </div>

    <!-- Chat Input Bar (Sits directly above the bottom tab bar) -->
    <div style="display:flex; gap:8px; align-items:center;">
      <button style="width:38px; height:38px; border:2px solid #000; border-radius:10px; background:#fff; display:flex; align-items:center; justify-content:center; box-shadow:2px 2px 0px #000;">
        <i data-lucide="paperclip" style="width:16px; height:16px;"></i>
      </button>
      <button style="width:38px; height:38px; border:2px solid #000; border-radius:10px; background:#fff; display:flex; align-items:center; justify-content:center; box-shadow:2px 2px 0px #000; color:#15803d;">
        <i data-lucide="mic" style="width:18px; height:18px;"></i>
      </button>
      <input type="text" placeholder="ಕನ್ನಡದಲ್ಲಿ ಕೇಳಿ ಅಥವಾ type in English..." style="flex:1; border:2px solid #000; border-radius:10px; padding:9px 12px; font-size:0.8rem; background:#fff; box-shadow:2px 2px 0px #000; outline:none;" readonly value="">
      <button style="width:38px; height:38px; border:2px solid #000; border-radius:10px; background:#15803d; color:#fff; display:flex; align-items:center; justify-content:center; box-shadow:2px 2px 0px #000;">
        <i data-lucide="send" style="width:16px; height:16px;"></i>
      </button>
    </div>
  </main>
''' + NAV_COMMON('chat')

# -----------------------------------------------------------------------------
# 7. Screen 7: Coffee Marketplace (Spacious, Large Text, Fully Filled to Bottom)
# -----------------------------------------------------------------------------
html_s7 = HEAD_COMMON + f'''
  <main class="page-content" style="gap: 8px; padding: 10px 14px 68px 14px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 style="font-size:1.25rem; font-weight:900; margin-bottom:2px;">Coffee Marketplace</h1>
        <p style="font-size:0.78rem; color:#4b5563;">Direct farmer-to-buyer trade. 0% platform commission.</p>
      </div>
      <button style="background:#15803d; color:#fff; border:2px solid #000; border-radius:8px; padding:6px 11px; font-size:0.76rem; font-weight:800; display:flex; align-items:center; gap:5px; box-shadow:2px 2px 0px #000;">
        <i data-lucide="plus" style="width:14px; height:14px;"></i> Post Lot
      </button>
    </div>

    <!-- Live Market Ticker -->
    <div style="background:#fef3c7; border:2px solid #000; border-radius:10px; padding:7px 12px; display:flex; justify-content:space-between; align-items:center; font-size:0.76rem; box-shadow:2px 2px 0px #000;">
      <span><strong>Karnataka APMC Mandi:</strong> Arabica Parchment</span>
      <span style="font-weight:900; color:#15803d; font-size:0.84rem;">₹14,500 / 50kg bag (▲ ₹250)</span>
    </div>

    <!-- Category Filter Tabs -->
    <div style="display:flex; gap:8px;">
      <span style="background:#15803d; color:#fff; border:1.5px solid #000; border-radius:8px; padding:5px 12px; font-size:0.76rem; font-weight:800;">All Lots (54)</span>
      <span style="background:#fff; border:1.5px solid #000; border-radius:8px; padding:5px 12px; font-size:0.76rem; font-weight:700;">Arabica (36)</span>
      <span style="background:#fff; border:1.5px solid #000; border-radius:8px; padding:5px 12px; font-size:0.76rem; font-weight:700;">Robusta (18)</span>
    </div>

    <!-- 6 Substantial Coffee Listings Flowing Down to Bottom Tab Bar -->
    <!-- Listing 1 -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; gap:10px; align-items:center;">
      <img src="{rust_b64}" style="width:52px; height:52px; border-radius:8px; object-fit:cover; border:1.5px solid #000; flex-shrink:0;">
      <div style="flex:1;">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
          <strong style="font-size:0.86rem;">Arabica Parchment (Grade A)</strong>
          <span style="font-weight:900; color:#15803d; font-size:0.9rem;">₹14,800/50kg</span>
        </div>
        <div style="font-size:0.74rem; color:#4b5563; margin:1px 0 4px 0;">Manjarabad Estate, Sakleshpur • 45 bags left</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.7rem; background:#dcfce7; color:#15803d; font-weight:800; padding:2px 7px; border-radius:5px; border:1px solid #15803d;">Direct WhatsApp</span>
          <button style="background:#2d5bff; color:#fff; border:1.5px solid #000; border-radius:6px; padding:4px 10px; font-size:0.74rem; font-weight:800;">Contact</button>
        </div>
      </div>
    </div>

    <!-- Listing 2 -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; gap:10px; align-items:center;">
      <img src="{healthy_b64}" style="width:52px; height:52px; border-radius:8px; object-fit:cover; border:1.5px solid #000; flex-shrink:0;">
      <div style="flex:1;">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
          <strong style="font-size:0.86rem;">Robusta Cherry (Clean Dry)</strong>
          <span style="font-weight:900; color:#15803d; font-size:0.9rem;">₹8,200/50kg</span>
        </div>
        <div style="font-size:0.74rem; color:#4b5563; margin:1px 0 4px 0;">Koppa Hills Organic Farm • 80 bags left</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.7rem; background:#eff6ff; color:#2563eb; font-weight:800; padding:2px 7px; border-radius:5px; border:1px solid #2563eb;">Direct Contact</span>
          <button style="background:#2d5bff; color:#fff; border:1.5px solid #000; border-radius:6px; padding:4px 10px; font-size:0.74rem; font-weight:800;">Contact</button>
        </div>
      </div>
    </div>

    <!-- Listing 3 -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; gap:10px; align-items:center;">
      <img src="{cercospora_b64}" style="width:52px; height:52px; border-radius:8px; object-fit:cover; border:1.5px solid #000; flex-shrink:0;">
      <div style="flex:1;">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
          <strong style="font-size:0.86rem;">Monsooned Malabar AA</strong>
          <span style="font-weight:900; color:#15803d; font-size:0.9rem;">₹16,200/50kg</span>
        </div>
        <div style="font-size:0.74rem; color:#4b5563; margin:1px 0 4px 0;">Baba Budangiri Highlands • 20 bags left</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.7rem; background:#fef3c7; color:#d97706; font-weight:800; padding:2px 7px; border-radius:5px; border:1px solid #d97706;">Specialty Grade</span>
          <button style="background:#2d5bff; color:#fff; border:1.5px solid #000; border-radius:6px; padding:4px 10px; font-size:0.74rem; font-weight:800;">Contact</button>
        </div>
      </div>
    </div>

    <!-- Listing 4 -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; gap:10px; align-items:center;">
      <img src="{rust_b64}" style="width:52px; height:52px; border-radius:8px; object-fit:cover; border:1.5px solid #000; flex-shrink:0;">
      <div style="flex:1;">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
          <strong style="font-size:0.86rem;">Green Coffee Arabica AAA</strong>
          <span style="font-weight:900; color:#15803d; font-size:0.9rem;">₹15,400/50kg</span>
        </div>
        <div style="font-size:0.74rem; color:#4b5563; margin:1px 0 4px 0;">Mudigere Estate Micro-lot • 35 bags left</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.7rem; background:#dcfce7; color:#15803d; font-weight:800; padding:2px 7px; border-radius:5px; border:1px solid #15803d;">Direct Call</span>
          <button style="background:#2d5bff; color:#fff; border:1.5px solid #000; border-radius:6px; padding:4px 10px; font-size:0.74rem; font-weight:800;">Contact</button>
        </div>
      </div>
    </div>

    <!-- Listing 5 -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; gap:10px; align-items:center;">
      <img src="{healthy_b64}" style="width:52px; height:52px; border-radius:8px; object-fit:cover; border:1.5px solid #000; flex-shrink:0;">
      <div style="flex:1;">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
          <strong style="font-size:0.86rem;">Plantation Peaberry (PB)</strong>
          <span style="font-weight:900; color:#15803d; font-size:0.9rem;">₹17,200/50kg</span>
        </div>
        <div style="font-size:0.74rem; color:#4b5563; margin:1px 0 4px 0;">Coorg Highland Estates • 28 bags left</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.7rem; background:#fef3c7; color:#d97706; font-weight:800; padding:2px 7px; border-radius:5px; border:1px solid #d97706;">Micro-Lot Reserve</span>
          <button style="background:#2d5bff; color:#fff; border:1.5px solid #000; border-radius:6px; padding:4px 10px; font-size:0.74rem; font-weight:800;">Contact</button>
        </div>
      </div>
    </div>

    <!-- Listing 6 -->
    <div style="border:2px solid #000; border-radius:12px; background:#fff; padding:8px 12px; box-shadow:2.5px 2.5px 0px #000; display:flex; gap:10px; align-items:center;">
      <img src="{cercospora_b64}" style="width:52px; height:52px; border-radius:8px; object-fit:cover; border:1.5px solid #000; flex-shrink:0;">
      <div style="flex:1;">
        <div style="display:flex; justify-content:space-between; align-items:baseline;">
          <strong style="font-size:0.86rem;">Robusta Parchment AB</strong>
          <span style="font-weight:900; color:#15803d; font-size:0.9rem;">₹9,600/50kg</span>
        </div>
        <div style="font-size:0.74rem; color:#4b5563; margin:1px 0 4px 0;">Kalasa Valley Coffee • 50 bags left</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.7rem; background:#eff6ff; color:#2563eb; font-weight:800; padding:2px 7px; border-radius:5px; border:1px solid #2563eb;">Direct Contact</span>
          <button style="background:#2d5bff; color:#fff; border:1.5px solid #000; border-radius:6px; padding:4px 10px; font-size:0.74rem; font-weight:800;">Contact</button>
        </div>
      </div>
    </div>

    <!-- Direct Trade Protection Strip (Sits flush right above bottom tab bar) -->
    <div style="border:2px solid #000; border-radius:10px; background:#fff; padding:7px 12px; box-shadow:2px 2px 0px #000; display:flex; justify-content:space-between; align-items:center; font-size:0.74rem;">
      <span style="color:#111827; font-weight:700;">🔒 Verified Planters & Exporters</span>
      <span style="color:#15803d; font-weight:800;">0% Commission Guarantee</span>
    </div>
  </main>
''' + NAV_COMMON('market')

# -----------------------------------------------------------------------------
# 8. Screen 8: Diagnostic History (Spacious, Large Text, Fully Filled to Bottom)
# -----------------------------------------------------------------------------
html_s8 = HEAD_COMMON + f'''
  <main class="page-content" style="gap: 8px; padding: 10px 14px 68px 14px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1 style="font-size:1.25rem; font-weight:900; margin-bottom:2px;">Diagnostic History</h1>
        <p style="font-size:0.78rem; color:#4b5563;">Chronological scans with verified CCRI advisories.</p>
      </div>
      <button style="background:#fff; border:1.5px solid #000; border-radius:8px; padding:5px 10px; font-size:0.74rem; font-weight:700; display:flex; align-items:center; gap:5px; box-shadow:1.5px 1.5px 0px #000;">
        <i data-lucide="filter" style="width:14px; height:14px;"></i> Filter
      </button>
    </div>

    <!-- Search & Archive Bar -->
    <div style="display:flex; gap:8px;">
      <input type="text" placeholder="Search diagnostic records & field notes..." style="flex:1; border:1.5px solid #000; border-radius:8px; padding:6px 12px; font-size:0.78rem; background:#fff; outline:none;" readonly value="">
      <span style="background:#f3f4f6; border:1.5px solid #000; border-radius:8px; padding:6px 10px; font-size:0.74rem; font-weight:800; display:flex; align-items:center;">7 Scans</span>
    </div>

    <!-- Monthly Diagnostic Summary Strip -->
    <div style="background:#eff6ff; border:1.5px solid #2563eb; border-radius:9px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center; font-size:0.74rem; color:#1e40af;">
      <span style="font-weight:700;">📅 October: 7 Field Scans Logged</span>
      <span style="font-weight:800; color:#15803d;">✓ 100% CCRI Grounded</span>
    </div>

    <!-- 7 Spacious History Scans Flowing Down to Tab Bar -->
    <!-- Item 1 -->
    <div style="border:2px solid #000; border-radius:11px; background:#fff; padding:7px 11px; box-shadow:2.5px 2.5px 0px #000; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{rust_b64}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; border:1.5px solid #000;">
        <div>
          <strong style="font-size:0.86rem; display:block;">Coffee Leaf Rust</strong>
          <span style="font-size:0.73rem; color:#b91c1c; font-weight:800;">96.4% • Severe • Today 10:14 AM</span>
          <span style="font-size:0.7rem; color:#6b7280; display:block;">Chikkamagaluru (980m) • Bordeaux 1%</span>
        </div>
      </div>
      <i data-lucide="chevron-right" style="width:16px; height:16px; color:#9ca3af;"></i>
    </div>

    <!-- Item 2 -->
    <div style="border:2px solid #000; border-radius:11px; background:#fff; padding:7px 11px; box-shadow:2.5px 2.5px 0px #000; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{healthy_b64}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; border:1.5px solid #000;">
        <div>
          <strong style="font-size:0.86rem; display:block;">Healthy Control Foliage</strong>
          <span style="font-size:0.73rem; color:#15803d; font-weight:800;">98.7% • Optimal • 03 Oct</span>
          <span style="font-size:0.7rem; color:#6b7280; display:block;">Baba Budan Giri • Normal Foliage</span>
        </div>
      </div>
      <i data-lucide="chevron-right" style="width:16px; height:16px; color:#9ca3af;"></i>
    </div>

    <!-- Item 3 -->
    <div style="border:2px solid #000; border-radius:11px; background:#fff; padding:7px 11px; box-shadow:2.5px 2.5px 0px #000; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{cercospora_b64}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; border:1.5px solid #000;">
        <div>
          <strong style="font-size:0.86rem; display:block;">Cercospora Leaf Spot</strong>
          <span style="font-size:0.73rem; color:#d97706; font-weight:800;">94.1% • Moderate • 28 Sep</span>
          <span style="font-size:0.7rem; color:#6b7280; display:block;">Mudigere • Copper Oxychloride 0.25%</span>
        </div>
      </div>
      <i data-lucide="chevron-right" style="width:16px; height:16px; color:#9ca3af;"></i>
    </div>

    <!-- Item 4 -->
    <div style="border:2px solid #000; border-radius:11px; background:#fff; padding:7px 11px; box-shadow:2.5px 2.5px 0px #000; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{rust_b64}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; border:1.5px solid #000;">
        <div>
          <strong style="font-size:0.86rem; display:block;">Coffee Leaf Miner</strong>
          <span style="font-size:0.73rem; color:#2563eb; font-weight:800;">91.8% • Mild • 19 Sep</span>
          <span style="font-size:0.7rem; color:#6b7280; display:block;">Sakleshpur • Neem Oil Spray</span>
        </div>
      </div>
      <i data-lucide="chevron-right" style="width:16px; height:16px; color:#9ca3af;"></i>
    </div>

    <!-- Item 5 -->
    <div style="border:2px solid #000; border-radius:11px; background:#fff; padding:7px 11px; box-shadow:2.5px 2.5px 0px #000; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{cercospora_b64}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; border:1.5px solid #000;">
        <div>
          <strong style="font-size:0.86rem; display:block;">Black Rot (Koleroga)</strong>
          <span style="font-size:0.73rem; color:#7c3aed; font-weight:800;">89.2% • Monsoonal • 12 Sep</span>
          <span style="font-size:0.7rem; color:#6b7280; display:block;">Balehonnur • Centered Pruning</span>
        </div>
      </div>
      <i data-lucide="chevron-right" style="width:16px; height:16px; color:#9ca3af;"></i>
    </div>

    <!-- Item 6 -->
    <div style="border:2px solid #000; border-radius:11px; background:#fff; padding:7px 11px; box-shadow:2.5px 2.5px 0px #000; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{rust_b64}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; border:1.5px solid #000;">
        <div>
          <strong style="font-size:0.86rem; display:block;">Anthracnose Twig Blight</strong>
          <span style="font-size:0.73rem; color:#d97706; font-weight:800;">92.5% • Post-Rain • 04 Sep</span>
          <span style="font-size:0.7rem; color:#6b7280; display:block;">Koppa Estate • Carbendazim 0.1%</span>
        </div>
      </div>
      <i data-lucide="chevron-right" style="width:16px; height:16px; color:#9ca3af;"></i>
    </div>

    <!-- Item 7 (Pre-harvest Berry Borer) -->
    <div style="border:2px solid #000; border-radius:11px; background:#fff; padding:7px 11px; box-shadow:2.5px 2.5px 0px #000; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:10px;">
        <img src="{healthy_b64}" style="width:40px; height:40px; border-radius:8px; object-fit:cover; border:1.5px solid #000;">
        <div>
          <strong style="font-size:0.86rem; display:block;">Coffee Berry Borer</strong>
          <span style="font-size:0.73rem; color:#2563eb; font-weight:800;">95.0% • Pre-Harvest • 22 Aug</span>
          <span style="font-size:0.7rem; color:#6b7280; display:block;">Kalasa Hills • Beauveria bassiana 1kg</span>
        </div>
      </div>
      <i data-lucide="chevron-right" style="width:16px; height:16px; color:#9ca3af;"></i>
    </div>

    <!-- Cloud Backup Strip -->
    <div style="border:1.5px solid #000; border-radius:10px; background:#fff; padding:6px 12px; box-shadow:1.5px 1.5px 0px #000; display:flex; justify-content:space-between; align-items:center; font-size:0.73rem;">
      <span style="color:#6b7280;">☁️ CCRI Planter Cloud: All 7 scans synchronized</span>
      <span style="color:#15803d; font-weight:800;">Online</span>
    </div>

    <!-- Undo Toast (Reaches directly above tab bar) -->
    <div style="background:#111827; color:#fff; border:2px solid #000; border-radius:10px; padding:7px 14px; display:flex; justify-content:space-between; align-items:center; font-size:0.76rem; box-shadow:2.5px 2.5px 0px #000;">
      <span>Scan saved to offline archive</span>
      <span style="color:#22c55e; font-weight:800; cursor:pointer;">UNDO (3s)</span>
    </div>
  </main>
''' + NAV_COMMON('history')

# Write HTML files
screens = [
    ("screen_01", html_s1),
    ("screen_02", html_s2),
    ("screen_03", html_s3),
    ("screen_04", html_s4),
    ("screen_05", html_s5),
    ("screen_06", html_s6),
    ("screen_07", html_s7),
    ("screen_08", html_s8),
]

for name, html in screens:
    snap_path = os.path.join(SNAP_DIR, f"{name}.html")
    with open(snap_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Updated {snap_path}")

# Capture screenshots using chrome-headless-shell
for name, _ in screens:
    snap_path = os.path.join(SNAP_DIR, f"{name}.html")
    out_png = os.path.join(OUT_DIR, f"{name}.png")
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=412,892",
        "--allow-file-access-from-files",
        f"--screenshot={out_png}",
        f"file:///{snap_path.replace(os.sep, '/')}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    size = os.path.getsize(out_png) if os.path.exists(out_png) else 0
    print(f"Captured {name}.png ({size} bytes)")

print("All 8 screens regenerated with increased text size and comfortable spacing!")
