"""
PlantIQ Mobile App Design Generator for A/B Testing
---------------------------------------------------
Generates 6 production-grade mobile screens (390x844 standard smartphone form factor)
tailored for Indian coffee smallholders and estate planters:
  1. 01_Leaf_Scanner_Home
  2. 02_Diagnosis_Advisory
  3. 03_Bilingual_Chatbot
  4. 04_Coffee_Marketplace
  5. 05_Create_Lot_Listing
  6. 06_History_and_Profile

Outputs:
  - figma-design/plantiq_mobile_redesign.figcraft
  - figma-design/plantiq_mobile_redesign.fig (Native Figma format)
  - figma-design/01_scanner.png, 02_diagnosis.png, etc.
  - figma-design/all_screens_preview.png
"""

import json
import os
import subprocess
import sys

FIGCRAFT_BIN = "C:/Users/solarquack/Downloads/figcraft/target/release/figcraft-cli.exe"
OUTPUT_DIR = "d:/end-capstone-project/cleaned/figma-design"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FIGCRAFT_FILE = os.path.join(OUTPUT_DIR, "plantiq_mobile_redesign.figcraft")

# Colors
C_BG = "#F8FAF7"
C_WHITE = "#FFFFFF"
C_PRIMARY = "#1B4332"       # Deep Plantation Forest Green
C_PRIMARY_MED = "#2D6A4F"   # Forest Green
C_PRIMARY_LIGHT = "#40916C" # Leaf Green
C_PRIMARY_TINT = "#E8F5E9"  # Mint Tint
C_ACCENT = "#C86D51"        # Coffee Cherry Terracotta
C_ACCENT_BG = "#FDF0ED"     # Soft Terracotta Tint
C_AMBER = "#D97706"         # Ochre Warning Amber
C_AMBER_BG = "#FEF3C7"      # Ochre Tint
C_EMERALD = "#059669"       # Success Leaf Emerald
C_EMERALD_BG = "#D1FAE5"    # Success Mint Tint
C_TEXT_DARK = "#1C2520"     # Espresso Slate
C_TEXT_MUTED = "#5A6B62"    # Muted Slate
C_TEXT_LIGHT = "#8C9E95"    # Subtle Slate
C_BORDER = "#E2E8F0"        # Card Border
C_CARD_BG = "#FFFFFF"

def run_commands(commands, in_file=None, out_file=FIGCRAFT_FILE):
    temp_json = os.path.join(OUTPUT_DIR, "_temp_cmd.json")
    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(commands, f, indent=2)

    args = [FIGCRAFT_BIN, "run", temp_json, "--out", out_file]
    if in_file and os.path.exists(in_file):
        args.extend(["--in", in_file])

    res = subprocess.run(args, capture_output=True, text=True)
    if os.path.exists(temp_json):
        os.remove(temp_json)

    if res.returncode != 0:
        print(f"Error running commands: {res.stderr}")
        return None

    # Parse JSON result lines
    results = []
    for line in res.stdout.strip().splitlines():
        if line.strip():
            try:
                results.append(json.loads(line))
            except Exception:
                pass
    return results


def build_all_screens():
    print("[*] Generating 6 Production Mobile Screens for PlantIQ A/B Test...")

    # Screen Coordinates (horizontal layout side by side)
    SCREEN_W = 390
    SCREEN_H = 844
    GAP = 50

    screens = [
        {"name": "01_Leaf_Scanner_Home", "title": "Field Scanner", "x": 0},
        {"name": "02_Diagnosis_Advisory", "title": "Diagnosis & CCRI Advisory", "x": (SCREEN_W + GAP) * 1},
        {"name": "03_Bilingual_Chatbot", "title": "Agri Agronomist Chat", "x": (SCREEN_W + GAP) * 2},
        {"name": "04_Coffee_Marketplace", "title": "Coffee Lot Marketplace", "x": (SCREEN_W + GAP) * 3},
        {"name": "05_Create_Lot_Listing", "title": "List Coffee Harvest Lot", "x": (SCREEN_W + GAP) * 4},
        {"name": "06_History_and_Profile", "title": "Field Records & Profile", "x": (SCREEN_W + GAP) * 5},
    ]

    # Stage 1: Create the 6 Root Mobile Frames
    create_frames = []
    for s in screens:
        create_frames.append({
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": s["name"],
                "x": s["x"],
                "y": 0,
                "width": SCREEN_W,
                "height": SCREEN_H,
                "props": {
                    "fill": C_BG,
                    "cornerRadius": 44,
                    "clip": True,
                    "effects": [{"type": "dropShadow", "color": "#00000015", "offset": [0, 8], "radius": 24}]
                }
            }
        })

    frame_results = run_commands(create_frames, in_file=None, out_file=FIGCRAFT_FILE)
    if not frame_results:
        print("[-] Failed to create root frames.")
        return

    frame_ids = [r["result"]["id"] for r in frame_results if r.get("ok")]
    print(f"[+] Created 6 Root Frames: {frame_ids}")

    # Map screen names to their frame IDs
    s_map = {screens[i]["name"]: frame_ids[i] for i in range(len(screens))}

    # Helper to add standard Status Bar & Bottom Nav Bar
    all_child_commands = []

    for name, f_id in s_map.items():
        # Status Bar (Top: 9:41, Cellular, Wifi, Battery)
        all_child_commands.extend([
            {
                "command": "node.create",
                "params": {
                    "type": "text",
                    "name": "StatusBarTime",
                    "parent": f_id,
                    "x": 32, "y": 14,
                    "text": "9:41",
                    "props": {"fontSize": 14, "fontWeight": 600, "fill": C_TEXT_DARK}
                }
            },
            {
                "command": "node.create",
                "params": {
                    "type": "text",
                    "name": "StatusBarIcons",
                    "parent": f_id,
                    "x": 300, "y": 14,
                    "text": "5G  ●  100%",
                    "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_MUTED}
                }
            }
        ])

    # ═════════════════════════════════════════════════════════════════════
    # SCREEN 1: 01_Leaf_Scanner_Home
    # ═════════════════════════════════════════════════════════════════════
    f1 = s_map["01_Leaf_Scanner_Home"]
    all_child_commands.extend([
        # Top App Header (Brand + Kannada Submark + Server Latency Pill)
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HeaderBrand",
                "parent": f1,
                "x": 24, "y": 48,
                "text": "PlantIQ 🌿 ಕಾಫಿ ಮಿತ್ರ",
                "props": {"fontSize": 20, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ServerStatusPill",
                "parent": f1,
                "x": 240, "y": 46, "width": 126, "height": 30,
                "props": {
                    "fill": C_EMERALD_BG,
                    "cornerRadius": 15,
                    "stroke": C_EMERALD,
                    "strokeWeight": 1
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ServerStatusText",
                "parent": f1,
                "x": 252, "y": 53,
                "text": "● Live (14ms)",
                "props": {"fontSize": 12, "fontWeight": 600, "fill": C_EMERALD}
            }
        },

        # Microclimate Weather Strip Card (Elevation, Temp, Humidity, Rain)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "WeatherCard",
                "parent": f1,
                "x": 20, "y": 90, "width": 350, "height": 72,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 20,
                    "stroke": C_BORDER,
                    "strokeWeight": 1,
                    "effects": [{"type": "dropShadow", "color": "#00000008", "offset": [0, 4], "radius": 12}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "WeatherLocation",
                "parent": f1,
                "x": 36, "y": 102,
                "text": "📍 Chikkamagaluru (13.3161°N, 75.7720°E) • 1,150m ASL",
                "props": {"fontSize": 12, "fontWeight": 600, "fill": C_PRIMARY_MED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "WeatherMetrics",
                "parent": f1,
                "x": 36, "y": 126,
                "text": "⛅ 24.2°C (Feels 26.5°C)  💧 84%  🌧️ 0.0mm  • High Risk",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },

        # Hero Viewfinder Card (Camera Leaf Scanning Zone)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ViewfinderFrame",
                "parent": f1,
                "x": 20, "y": 178, "width": 350, "height": 360,
                "props": {
                    "fill": "#0A1F16",
                    "cornerRadius": 28,
                    "stroke": C_PRIMARY_LIGHT,
                    "strokeWeight": 2,
                    "clip": True
                }
            }
        },
        # Viewfinder simulated leaf outline
        {
            "command": "node.create",
            "params": {
                "type": "ellipse",
                "name": "LeafGuideGlow",
                "parent": f1,
                "x": 115, "y": 240, "width": 160, "height": 210,
                "props": {
                    "fill": "#1B433240",
                    "stroke": C_PRIMARY_LIGHT,
                    "strokeWeight": 2,
                    "dashes": [6, 6]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LeafGuideInstruction",
                "parent": f1,
                "x": 50, "y": 460, "width": 290,
                "text": "Hold camera 15-20cm from coffee leaf\nಎಲೆಯನ್ನು ಚೌಕಟ್ಟಿನಲ್ಲಿ ಸ್ಪಷ್ಟವಾಗಿ ಇರಿಸಿ",
                "props": {"fontSize": 13, "fontWeight": 500, "fill": "#A7F3D0", "textAlign": "center"}
            }
        },
        # Scan Reticles (Corner brackets)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ReticleTopLeft",
                "parent": f1,
                "x": 40, "y": 198, "width": 32, "height": 32,
                "props": {"stroke": C_EMERALD, "strokeWeight": 3, "strokeSides": [True, False, False, True], "cornerRadius": 4}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ReticleTopRight",
                "parent": f1,
                "x": 318, "y": 198, "width": 32, "height": 32,
                "props": {"stroke": C_EMERALD, "strokeWeight": 3, "strokeSides": [True, True, False, False], "cornerRadius": 4}
            }
        },

        # Shutter Action Row
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "GalleryBtn",
                "parent": f1,
                "x": 56, "y": 560, "width": 56, "height": 56,
                "props": {"fill": C_WHITE, "cornerRadius": 28, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "GalleryIcon",
                "parent": f1,
                "x": 72, "y": 578,
                "text": "🖼️",
                "props": {"fontSize": 18}
            }
        },
        # Big Center Shutter Button
        {
            "command": "node.create",
            "params": {
                "type": "ellipse",
                "name": "ShutterOuterRing",
                "parent": f1,
                "x": 155, "y": 550, "width": 78, "height": 78,
                "props": {"stroke": C_PRIMARY_LIGHT, "strokeWeight": 3, "fill": "#00000000"}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "ellipse",
                "name": "ShutterInner",
                "parent": f1,
                "x": 162, "y": 557, "width": 64, "height": 64,
                "props": {"fill": C_PRIMARY, "effects": [{"type": "dropShadow", "color": "#1B433260", "offset": [0, 4], "radius": 12}]}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ShutterIcon",
                "parent": f1,
                "x": 184, "y": 577,
                "text": "📷",
                "props": {"fontSize": 22}
            }
        },
        # Flash button
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "FlashBtn",
                "parent": f1,
                "x": 278, "y": 560, "width": 56, "height": 56,
                "props": {"fill": C_WHITE, "cornerRadius": 28, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "FlashIcon",
                "parent": f1,
                "x": 296, "y": 578,
                "text": "⚡",
                "props": {"fontSize": 18}
            }
        },

        # Recent Disease Alert Banner
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "RustAlertCard",
                "parent": f1,
                "x": 20, "y": 644, "width": 350, "height": 92,
                "props": {
                    "fill": C_AMBER_BG,
                    "cornerRadius": 18,
                    "stroke": C_AMBER,
                    "strokeWeight": 1
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "RustAlertTitle",
                "parent": f1,
                "x": 36, "y": 656,
                "text": "⚠️ Coffee Leaf Rust Outbreak Alert (ತುಕ್ಕು ರೋಗ)",
                "props": {"fontSize": 13, "fontWeight": 700, "fill": C_AMBER}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "RustAlertBody",
                "parent": f1,
                "x": 36, "y": 678, "width": 318,
                "text": "High humidity (84%) creates peak sporulation risk in Balehonnur. Inspect underside of leaves for orange pustules.",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": "#78350F"}
            }
        },

        # Bottom Navigation Bar
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "BottomNav",
                "parent": f1,
                "x": 0, "y": 756, "width": 390, "height": 88,
                "props": {"fill": C_WHITE, "stroke": C_BORDER, "strokeWeight": 1, "strokeSides": [True, False, False, False]}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "NavTabScanActive",
                "parent": f1,
                "x": 20, "y": 768, "width": 64, "height": 56,
                "props": {"fill": C_PRIMARY_TINT, "cornerRadius": 16}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "NavTabScanText",
                "parent": f1,
                "x": 36, "y": 776,
                "text": "🌿\nScan",
                "props": {"fontSize": 11, "fontWeight": 700, "fill": C_PRIMARY, "textAlign": "center"}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "NavTabChat",
                "parent": f1,
                "x": 108, "y": 776,
                "text": "💬\nChat",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_MUTED, "textAlign": "center"}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "NavTabMarket",
                "parent": f1,
                "x": 180, "y": 776,
                "text": "🛒\nMarket",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_MUTED, "textAlign": "center"}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "NavTabHistory",
                "parent": f1,
                "x": 252, "y": 776,
                "text": "📜\nHistory",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_MUTED, "textAlign": "center"}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "NavTabProfile",
                "parent": f1,
                "x": 324, "y": 776,
                "text": "👤\nProfile",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_MUTED, "textAlign": "center"}
            }
        }
    ])

    # ═════════════════════════════════════════════════════════════════════
    # SCREEN 2: 02_Diagnosis_Advisory
    # ═════════════════════════════════════════════════════════════════════
    f2 = s_map["02_Diagnosis_Advisory"]
    all_child_commands.extend([
        # Top Header (Back + Title + Share)
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "BackBtn",
                "parent": f2,
                "x": 24, "y": 48,
                "text": "← Back",
                "props": {"fontSize": 15, "fontWeight": 600, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "DiagTitle",
                "parent": f2,
                "x": 130, "y": 48,
                "text": "Diagnostic Report",
                "props": {"fontSize": 16, "fontWeight": 700, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ShareBtn",
                "parent": f2,
                "x": 330, "y": 48,
                "text": "↗️",
                "props": {"fontSize": 18}
            }
        },

        # Diagnosis Hero Card (Disease Name + Confidence)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "DiseaseHeroCard",
                "parent": f2,
                "x": 20, "y": 86, "width": 350, "height": 130,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 24,
                    "stroke": C_BORDER,
                    "strokeWeight": 1,
                    "effects": [{"type": "dropShadow", "color": "#0000000A", "offset": [0, 4], "radius": 16}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "DiseaseBadgePill",
                "parent": f2,
                "x": 36, "y": 102, "width": 170, "height": 28,
                "props": {"fill": C_AMBER_BG, "cornerRadius": 14}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "DiseaseBadgeText",
                "parent": f2,
                "x": 48, "y": 108,
                "text": "⚠️ FUNGAL PATHOLOGY",
                "props": {"fontSize": 11, "fontWeight": 700, "fill": C_AMBER}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "DiseaseName",
                "parent": f2,
                "x": 36, "y": 138,
                "text": "Coffee Leaf Rust (CLR)\nಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ",
                "props": {"fontSize": 18, "fontWeight": 700, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ConfidenceScore",
                "parent": f2,
                "x": 260, "y": 120,
                "text": "94.8%\nAccuracy",
                "props": {"fontSize": 16, "fontWeight": 700, "fill": C_AMBER, "textAlign": "center"}
            }
        },

        # Probability Breakdown Bar
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ProbBarBg",
                "parent": f2,
                "x": 36, "y": 194, "width": 318, "height": 8,
                "props": {"fill": "#E5E7EB", "cornerRadius": 4}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ProbBarFill",
                "parent": f2,
                "x": 36, "y": 194, "width": 301, "height": 8, # 94.8%
                "props": {"fill": C_AMBER, "cornerRadius": 4}
            }
        },

        # Upgraded 3-Stage Hybrid RAG Advisory Card
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "AdvisoryCard",
                "parent": f2,
                "x": 20, "y": 230, "width": 350, "height": 380,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 24,
                    "stroke": C_BORDER,
                    "strokeWeight": 1,
                    "effects": [{"type": "dropShadow", "color": "#0000000A", "offset": [0, 4], "radius": 16}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "AdvisoryHeader",
                "parent": f2,
                "x": 36, "y": 246,
                "text": "📚 CCRI Actionable Advisory (ಔಷಧಿ ವಿವರ)",
                "props": {"fontSize": 15, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ChemicalSchedule",
                "parent": f2,
                "x": 36, "y": 278, "width": 318,
                "text": "1. Chemical Spray Formulation (ರಾಸಾಯನಿಕ ಔಷಧ):\n   • Bordeaux Mixture 1% (2 kg CuSO4 + 2 kg lime in 200L barrel)\n   • Or Contaf 5% EC (Hexaconazole) @ 400 ml per 200L barrel.\n\n2. Application Window (ಸಿಂಪಡಣೆ ಸಮಯ):\n   • Pre-monsoon spray in May-June before Southwest monsoon.",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "CanopyManagement",
                "parent": f2,
                "x": 36, "y": 390, "width": 318,
                "text": "3. Cultural Canopy Practice (ನೆರಳು ನಿರ್ವಹಣೆ):\n   • Lop lower dadap shade branches to maximize airflow.\n   • Remove heavily rusted fallen leaves from estate floor.",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },

        # Safety Verification Audit Guardrail Box
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "SafetyGuardrailBox",
                "parent": f2,
                "x": 36, "y": 480, "width": 318, "height": 60,
                "props": {
                    "fill": C_EMERALD_BG,
                    "cornerRadius": 14,
                    "stroke": C_EMERALD,
                    "strokeWeight": 1
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "SafetyGuardrailText",
                "parent": f2,
                "x": 48, "y": 490, "width": 294,
                "text": "✓ CCRI Dosage Guardrail Verified (100% Literature Match)\nAudited: 1% dilution & 400ml/200L confirmed by Central Coffee Institute.",
                "props": {"fontSize": 10, "fontWeight": 600, "fill": "#065F46"}
            }
        },

        # Citation Badge
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "CitationFooter",
                "parent": f2,
                "x": 36, "y": 558, "width": 318,
                "text": "📖 Source: Strategies for Coffee Leaf Rust Management, Page 4",
                "props": {"fontSize": 10, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },

        # Action Buttons (Chat with Agronomist + WhatsApp Share)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "AskAgronomistBtn",
                "parent": f2,
                "x": 20, "y": 630, "width": 350, "height": 52,
                "props": {
                    "fill": C_ACCENT,
                    "cornerRadius": 26,
                    "effects": [{"type": "dropShadow", "color": "#C86D5140", "offset": [0, 4], "radius": 12}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "AskAgronomistBtnText",
                "parent": f2,
                "x": 90, "y": 646,
                "text": "💬 Ask Agronomist About This Scan",
                "props": {"fontSize": 14, "fontWeight": 700, "fill": C_WHITE}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "WhatsAppShareBtn",
                "parent": f2,
                "x": 20, "y": 694, "width": 350, "height": 48,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 24,
                    "stroke": C_BORDER,
                    "strokeWeight": 1
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "WhatsAppShareBtnText",
                "parent": f2,
                "x": 105, "y": 708,
                "text": "📱 Share Report to WhatsApp",
                "props": {"fontSize": 13, "fontWeight": 600, "fill": C_PRIMARY}
            }
        }
    ])

    # ═════════════════════════════════════════════════════════════════════
    # SCREEN 3: 03_Bilingual_Chatbot
    # ═════════════════════════════════════════════════════════════════════
    f3 = s_map["03_Bilingual_Chatbot"]
    all_child_commands.extend([
        # Header (PlantIQ Agronomist + Active Context)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ChatHeaderBg",
                "parent": f3,
                "x": 0, "y": 38, "width": 390, "height": 68,
                "props": {"fill": C_WHITE, "stroke": C_BORDER, "strokeWeight": 1, "strokeSides": [False, False, True, False]}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ChatTitle",
                "parent": f3,
                "x": 24, "y": 48,
                "text": "PlantIQ Agri-Advisor 🤖",
                "props": {"fontSize": 17, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ChatSub",
                "parent": f3,
                "x": 24, "y": 72,
                "text": "📍 12.4244°N, 75.7382°E (Manual) • 23.1°C 93% Humid",
                "props": {"fontSize": 11, "fontWeight": 600, "fill": C_PRIMARY_MED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LangSwitchPill",
                "parent": f3,
                "x": 290, "y": 52, "width": 78, "height": 30,
                "props": {"fill": C_PRIMARY_TINT, "cornerRadius": 15, "stroke": C_PRIMARY_LIGHT, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LangSwitchText",
                "parent": f3,
                "x": 304, "y": 59,
                "text": "ಕನ್ನಡ",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },

        # System Greeting
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "SystemBubble",
                "parent": f3,
                "x": 30, "y": 120, "width": 330, "height": 52,
                "props": {"fill": "#E2E8F0", "cornerRadius": 16}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "SystemBubbleText",
                "parent": f3,
                "x": 42, "y": 128, "width": 306,
                "text": "🌱 ನಮಸ್ಕಾರ ಮಂಜುನಾಥ್! ನಿಮ್ಮ ಕಾಫಿ ಎಲೆ ರೋಗ ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಯಾವುದೇ ಪ್ರಶ್ನೆ ಕೇಳಿ.",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },

        # User Message (with Photo Attachment Thumbnail)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "UserBubble",
                "parent": f3,
                "x": 100, "y": 190, "width": 270, "height": 130,
                "props": {"fill": C_PRIMARY, "cornerRadius": 20}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "AttachedPhotoThumb",
                "parent": f3,
                "x": 114, "y": 204, "width": 64, "height": 52,
                "props": {"fill": "#2D6A4F", "cornerRadius": 12, "stroke": "#40916C", "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "AttachedPhotoIcon",
                "parent": f3,
                "x": 134, "y": 220,
                "text": "🍃",
                "props": {"fontSize": 18}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "UserQueryText",
                "parent": f3,
                "x": 114, "y": 268, "width": 242,
                "text": "ಈ ಎಲೆಗೆ 200 ಲೀಟರ್ ಬ್ಯಾರೆಲ್‌ಗೆ ಎಷ್ಟು ಬೋರ್ಡೋ ದ್ರಾವಣ ಹಾಕಬೇಕು?",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_WHITE}
            }
        },

        # AI Agronomist Response Bubble (Bilingual Kannada & English RAG advisory)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "BotBubble",
                "parent": f3,
                "x": 20, "y": 336, "width": 340, "height": 260,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 22,
                    "stroke": C_BORDER,
                    "strokeWeight": 1,
                    "effects": [{"type": "dropShadow", "color": "#00000008", "offset": [0, 4], "radius": 12}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "BotResponseText",
                "parent": f3,
                "x": 36, "y": 352, "width": 308,
                "text": "🌿 ಕಾಫಿ ಸಂಶೋಧನಾ ಸಂಸ್ಥೆ (CCRI) ಶಿಫಾರಸು:\n\n• 200 ಲೀಟರ್ ನೀರಿಗೆ: 2 ಕೆಜಿ ತಾಮ್ರದ ಸಲ್ಫೇಟ್ (ಮೈಲುತುತ್ತ) + 2 ಕೆಜಿ ಅರಳಿಸಿದ ಸುಣ್ಣ ಬಳಸಿ (1% ದ್ರಾವಣ).\n• ಅಥವಾ Hexaconazole 5% EC (Contaf) @ 400 ಮಿ.ಲೀ / ಬ್ಯಾರೆಲ್.\n• ಮುಂಗಾರು ಮಳೆ ಆರಂಭವಾಗುವ ಮುನ್ನ (ಮೇ-ಜೂನ್) ಎಲೆಯ ಹಿಂಭಾಗಕ್ಕೆ ಬೀಳುವಂತೆ ಸಿಂಪಡಿಸಿ.",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },
        # Audio Playback Pill in Bot Bubble
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "AudioListenPill",
                "parent": f3,
                "x": 36, "y": 490, "width": 170, "height": 34,
                "props": {"fill": C_PRIMARY_TINT, "cornerRadius": 17, "stroke": C_PRIMARY_MED, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "AudioListenText",
                "parent": f3,
                "x": 50, "y": 499,
                "text": "🔊 ಕನ್ನಡದಲ್ಲಿ ಆಲಿಸಿ (Voice)",
                "props": {"fontSize": 11, "fontWeight": 600, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "BotCitation",
                "parent": f3,
                "x": 36, "y": 556, "width": 308,
                "text": "📖 ಆಧಾರ: CCRI Manual Page 14 • 100% ಸಾಹಿತ್ಯ ಪರಿಶೀಲಿತ",
                "props": {"fontSize": 10, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },

        # Bottom Multimodal Dock (Audio Record + Camera + Text Input)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ChatDockBg",
                "parent": f3,
                "x": 0, "y": 750, "width": 390, "height": 94,
                "props": {"fill": C_WHITE, "stroke": C_BORDER, "strokeWeight": 1, "strokeSides": [True, False, False, False]}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ChatTextInputBox",
                "parent": f3,
                "x": 16, "y": 762, "width": 240, "height": 48,
                "props": {"fill": "#F1F5F9", "cornerRadius": 24, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ChatPlaceholder",
                "parent": f3,
                "x": 32, "y": 778,
                "text": "ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ / ಟೈಪ್ ಮಾಡಿ...",
                "props": {"fontSize": 12, "fontWeight": 400, "fill": C_TEXT_LIGHT}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "CameraAttachBtn",
                "parent": f3,
                "x": 264, "y": 762, "width": 48, "height": 48,
                "props": {"fill": C_WHITE, "cornerRadius": 24, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "CameraAttachIcon",
                "parent": f3,
                "x": 279, "y": 776,
                "text": "📷",
                "props": {"fontSize": 16}
            }
        },
        # Big Prominent Audio Mic Button (IndicConformer STT trigger)
        {
            "command": "node.create",
            "params": {
                "type": "ellipse",
                "name": "AudioMicBtn",
                "parent": f3,
                "x": 320, "y": 760, "width": 52, "height": 52,
                "props": {"fill": C_PRIMARY, "effects": [{"type": "dropShadow", "color": "#1B433250", "offset": [0, 4], "radius": 10}]}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "AudioMicIcon",
                "parent": f3,
                "x": 338, "y": 776,
                "text": "🎙️",
                "props": {"fontSize": 18}
            }
        }
    ])

    # ═════════════════════════════════════════════════════════════════════
    # SCREEN 4: 04_Coffee_Marketplace
    # ═════════════════════════════════════════════════════════════════════
    f4 = s_map["04_Coffee_Marketplace"]
    all_child_commands.extend([
        # Header (Marketplace Title + Balehonnur Hub)
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "MarketTitle",
                "parent": f4,
                "x": 24, "y": 48,
                "text": "Coffee Marketplace 🛒",
                "props": {"fontSize": 20, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "MarketSub",
                "parent": f4,
                "x": 24, "y": 74,
                "text": "Karnataka Coffee Belt (Chikkamagaluru / Kodagu)",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },

        # Segmented Mode Switcher (Browse Lots vs My Listings)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "SegmentedSwitchBg",
                "parent": f4,
                "x": 20, "y": 102, "width": 350, "height": 44,
                "props": {"fill": "#E2E8F0", "cornerRadius": 22}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "SegmentActivePill",
                "parent": f4,
                "x": 24, "y": 106, "width": 170, "height": 36,
                "props": {"fill": C_WHITE, "cornerRadius": 18, "effects": [{"type": "dropShadow", "color": "#00000010", "offset": [0, 2], "radius": 6}]}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "SegmentActiveText",
                "parent": f4,
                "x": 48, "y": 116,
                "text": "Browse Harvest Lots",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "SegmentInactiveText",
                "parent": f4,
                "x": 218, "y": 116,
                "text": "My Listings (3)",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },

        # Filter Chips Bar (Cultivar selector)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ChipAll",
                "parent": f4,
                "x": 20, "y": 156, "width": 78, "height": 32,
                "props": {"fill": C_PRIMARY, "cornerRadius": 16}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ChipAllText",
                "parent": f4,
                "x": 34, "y": 164,
                "text": "All Lots",
                "props": {"fontSize": 11, "fontWeight": 600, "fill": C_WHITE}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ChipArabica",
                "parent": f4,
                "x": 106, "y": 156, "width": 136, "height": 32,
                "props": {"fill": C_WHITE, "cornerRadius": 16, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ChipArabicaText",
                "parent": f4,
                "x": 118, "y": 164,
                "text": "Arabica Parchment",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ChipRobusta",
                "parent": f4,
                "x": 250, "y": 156, "width": 115, "height": 32,
                "props": {"fill": C_WHITE, "cornerRadius": 16, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ChipRobustaText",
                "parent": f4,
                "x": 264, "y": 164,
                "text": "Robusta Cherry",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },

        # Marketplace Listing Card 1 (Arabica Plantation A)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LotCard1",
                "parent": f4,
                "x": 20, "y": 202, "width": 350, "height": 236,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 22,
                    "stroke": C_BORDER,
                    "strokeWeight": 1,
                    "effects": [{"type": "dropShadow", "color": "#00000008", "offset": [0, 4], "radius": 14}]
                }
            }
        },
        # Photo placeholder frame
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LotPhoto1",
                "parent": f4,
                "x": 32, "y": 214, "width": 326, "height": 84,
                "props": {"fill": "#2D6A4F20", "cornerRadius": 14}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LotPhotoIcon1",
                "parent": f4,
                "x": 130, "y": 248,
                "text": "☕ Arabica Washed Parchment",
                "props": {"fontSize": 13, "fontWeight": 600, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LotPrice1",
                "parent": f4,
                "x": 36, "y": 308,
                "text": "₹8,850 / 50kg bag",
                "props": {"fontSize": 17, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LotDetails1",
                "parent": f4,
                "x": 36, "y": 332,
                "text": "Volume: 45 Bags (2,250 kg)  •  Moisture: 10.4%\nDevadhanam Estate, Mudigere  •  1,180m ASL (4 km)",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },
        # 1-Tap CTAs (WhatsApp + Call)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "WhatsAppBtn1",
                "parent": f4,
                "x": 36, "y": 380, "width": 190, "height": 42,
                "props": {"fill": "#25D366", "cornerRadius": 21}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "WhatsAppBtnText1",
                "parent": f4,
                "x": 56, "y": 393,
                "text": "💬 WhatsApp Planter",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": C_WHITE}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "CallBtn1",
                "parent": f4,
                "x": 236, "y": 380, "width": 120, "height": 42,
                "props": {"fill": C_WHITE, "cornerRadius": 21, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "CallBtnText1",
                "parent": f4,
                "x": 266, "y": 393,
                "text": "📞 Call",
                "props": {"fontSize": 12, "fontWeight": 600, "fill": C_TEXT_DARK}
            }
        },

        # Marketplace Listing Card 2 (Robusta Cherry AB)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LotCard2",
                "parent": f4,
                "x": 20, "y": 454, "width": 350, "height": 220,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 22,
                    "stroke": C_BORDER,
                    "strokeWeight": 1,
                    "effects": [{"type": "dropShadow", "color": "#00000008", "offset": [0, 4], "radius": 14}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LotPhoto2",
                "parent": f4,
                "x": 32, "y": 466, "width": 326, "height": 72,
                "props": {"fill": "#C86D5120", "cornerRadius": 14}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LotPhotoIcon2",
                "parent": f4,
                "x": 136, "y": 492,
                "text": "🍒 Robusta Sun-Dried Cherry",
                "props": {"fontSize": 13, "fontWeight": 600, "fill": C_ACCENT}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LotPrice2",
                "parent": f4,
                "x": 36, "y": 550,
                "text": "₹6,400 / 50kg bag",
                "props": {"fontSize": 17, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LotDetails2",
                "parent": f4,
                "x": 36, "y": 574,
                "text": "Volume: 80 Bags (4,000 kg)  •  Moisture: 11.2%\nCoorg Green Valley, Somwarpet  •  920m ASL",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "WhatsAppBtn2",
                "parent": f4,
                "x": 36, "y": 616, "width": 190, "height": 42,
                "props": {"fill": "#25D366", "cornerRadius": 21}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "WhatsAppBtnText2",
                "parent": f4,
                "x": 56, "y": 629,
                "text": "💬 WhatsApp Planter",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": C_WHITE}
            }
        },

        # Floating Action Button (+ List Your Harvest)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "CreateListingFAB",
                "parent": f4,
                "x": 105, "y": 696, "width": 180, "height": 50,
                "props": {
                    "fill": C_ACCENT,
                    "cornerRadius": 25,
                    "effects": [{"type": "dropShadow", "color": "#C86D5150", "offset": [0, 6], "radius": 16}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "CreateListingFABText",
                "parent": f4,
                "x": 124, "y": 712,
                "text": "➕ List Coffee Lot",
                "props": {"fontSize": 14, "fontWeight": 700, "fill": C_WHITE}
            }
        }
    ])

    # ═════════════════════════════════════════════════════════════════════
    # SCREEN 5: 05_Create_Lot_Listing
    # ═════════════════════════════════════════════════════════════════════
    f5 = s_map["05_Create_Lot_Listing"]
    all_child_commands.extend([
        # Header
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ListingHeaderBack",
                "parent": f5,
                "x": 24, "y": 48,
                "text": "← Cancel",
                "props": {"fontSize": 14, "fontWeight": 600, "fill": C_TEXT_MUTED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ListingHeaderTitle",
                "parent": f5,
                "x": 120, "y": 48,
                "text": "List Harvest Lot",
                "props": {"fontSize": 16, "fontWeight": 700, "fill": C_TEXT_DARK}
            }
        },

        # Step 1: Multi-Photo Upload Area
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "PhotoUploadBox",
                "parent": f5,
                "x": 20, "y": 88, "width": 350, "height": 110,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 18,
                    "stroke": C_PRIMARY_LIGHT,
                    "strokeWeight": 2,
                    "dashes": [6, 4]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PhotoUploadText",
                "parent": f5,
                "x": 70, "y": 126,
                "text": "📷 Tap to Upload Lot Photos (Up to 4 Photos)\nDrying yard, Parchment & Bean Closeups",
                "props": {"fontSize": 12, "fontWeight": 600, "fill": C_PRIMARY_MED, "textAlign": "center"}
            }
        },

        # Form Field 1: Coffee Species (Arabica / Robusta)
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "FieldSpeciesLabel",
                "parent": f5,
                "x": 24, "y": 218,
                "text": "Coffee Species (ಕಾಫಿ ತಳಿ)",
                "props": {"fontSize": 13, "fontWeight": 600, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "RadioArabicaSelected",
                "parent": f5,
                "x": 20, "y": 240, "width": 168, "height": 44,
                "props": {"fill": C_PRIMARY_TINT, "cornerRadius": 12, "stroke": C_PRIMARY, "strokeWeight": 2}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "RadioArabicaText",
                "parent": f5,
                "x": 44, "y": 254,
                "text": "● Arabica (ಅರೇಬಿಕಾ)",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "RadioRobusta",
                "parent": f5,
                "x": 202, "y": 240, "width": 168, "height": 44,
                "props": {"fill": C_WHITE, "cornerRadius": 12, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "RadioRobustaText",
                "parent": f5,
                "x": 226, "y": 254,
                "text": "○ Robusta (ರೋಬಸ್ಟಾ)",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },

        # Form Field 2: Processing Grade
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "FieldGradeLabel",
                "parent": f5,
                "x": 24, "y": 302,
                "text": "Processing Method & Grade",
                "props": {"fontSize": 13, "fontWeight": 600, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "GradeInputBox",
                "parent": f5,
                "x": 20, "y": 324, "width": 350, "height": 48,
                "props": {"fill": C_WHITE, "cornerRadius": 14, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "GradeInputValue",
                "parent": f5,
                "x": 36, "y": 338,
                "text": "Washed Parchment (Plantation A - Shade Grown)",
                "props": {"fontSize": 13, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },

        # Form Field 3: Lot Economics (Quantity + Price)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "QtyInputBox",
                "parent": f5,
                "x": 20, "y": 390, "width": 168, "height": 56,
                "props": {"fill": C_WHITE, "cornerRadius": 14, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "QtyLabel",
                "parent": f5,
                "x": 32, "y": 398,
                "text": "Lot Quantity (Bags)",
                "props": {"fontSize": 10, "fontWeight": 600, "fill": C_TEXT_MUTED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "QtyVal",
                "parent": f5,
                "x": 32, "y": 418,
                "text": "50 Bags (50kg)",
                "props": {"fontSize": 14, "fontWeight": 700, "fill": C_TEXT_DARK}
            }
        },

        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "PriceInputBox",
                "parent": f5,
                "x": 202, "y": 390, "width": 168, "height": 56,
                "props": {"fill": C_WHITE, "cornerRadius": 14, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PriceLabel",
                "parent": f5,
                "x": 214, "y": 398,
                "text": "Price per Bag (₹)",
                "props": {"fontSize": 10, "fontWeight": 600, "fill": C_TEXT_MUTED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PriceVal",
                "parent": f5,
                "x": 214, "y": 418,
                "text": "₹ 8,900 / Bag",
                "props": {"fontSize": 14, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },

        # Form Field 4: Estate Location (GPS auto capture)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "GpsBox",
                "parent": f5,
                "x": 20, "y": 466, "width": 350, "height": 72,
                "props": {"fill": C_EMERALD_BG, "cornerRadius": 16, "stroke": C_EMERALD, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "GpsTitle",
                "parent": f5,
                "x": 36, "y": 478,
                "text": "📍 GPS Estate Coordinates Captured",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": "#065F46"}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "GpsSub",
                "parent": f5,
                "x": 36, "y": 500,
                "text": "Silver Springs Estate • Balehonnur (13.315° N, 75.775° E)",
                "props": {"fontSize": 11, "fontWeight": 500, "fill": C_TEXT_DARK}
            }
        },

        # Form Field 5: WhatsApp Direct Inquiry Toggle
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "WhatsAppToggleCard",
                "parent": f5,
                "x": 20, "y": 558, "width": 350, "height": 60,
                "props": {"fill": C_WHITE, "cornerRadius": 16, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "WhatsAppToggleText",
                "parent": f5,
                "x": 36, "y": 578,
                "text": "Allow Verified Buyers to WhatsApp Directly",
                "props": {"fontSize": 12, "fontWeight": 600, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "ToggleSwitchPill",
                "parent": f5,
                "x": 310, "y": 574, "width": 46, "height": 26,
                "props": {"fill": "#25D366", "cornerRadius": 13}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "ellipse",
                "name": "ToggleSwitchKnob",
                "parent": f5,
                "x": 332, "y": 576, "width": 22, "height": 22,
                "props": {"fill": C_WHITE}
            }
        },

        # Submit Button
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "PublishLotBtn",
                "parent": f5,
                "x": 20, "y": 660, "width": 350, "height": 56,
                "props": {
                    "fill": C_PRIMARY,
                    "cornerRadius": 28,
                    "effects": [{"type": "dropShadow", "color": "#1B433240", "offset": [0, 4], "radius": 14}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PublishLotBtnText",
                "parent": f5,
                "x": 95, "y": 678,
                "text": "Publish Harvest Lot (ಲಾಟ್ ಪ್ರಕಟಿಸಿ)",
                "props": {"fontSize": 14, "fontWeight": 700, "fill": C_WHITE}
            }
        }
    ])

    # ═════════════════════════════════════════════════════════════════════
    # SCREEN 6: 06_History_and_Profile
    # ═════════════════════════════════════════════════════════════════════
    f6 = s_map["06_History_and_Profile"]
    all_child_commands.extend([
        # Header
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "ProfileHeaderTitle",
                "parent": f6,
                "x": 24, "y": 48,
                "text": "Planter Records & Profile",
                "props": {"fontSize": 20, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },

        # Planter Identity Card
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "PlanterIdCard",
                "parent": f6,
                "x": 20, "y": 88, "width": 350, "height": 96,
                "props": {
                    "fill": C_WHITE,
                    "cornerRadius": 22,
                    "stroke": C_BORDER,
                    "strokeWeight": 1,
                    "effects": [{"type": "dropShadow", "color": "#00000008", "offset": [0, 4], "radius": 12}]
                }
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "ellipse",
                "name": "PlanterAvatar",
                "parent": f6,
                "x": 36, "y": 106, "width": 60, "height": 60,
                "props": {"fill": C_PRIMARY_TINT, "stroke": C_PRIMARY_LIGHT, "strokeWeight": 2}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PlanterAvatarLetter",
                "parent": f6,
                "x": 58, "y": 122,
                "text": "M",
                "props": {"fontSize": 22, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PlanterName",
                "parent": f6,
                "x": 110, "y": 106,
                "text": "Manjunath Gowda (ಮಂಜುನಾಥ್)",
                "props": {"fontSize": 15, "fontWeight": 700, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PlanterEstate",
                "parent": f6,
                "x": 110, "y": 128,
                "text": "Silver Springs Estate • Balehonnur",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "PlanterVerifiedBadge",
                "parent": f6,
                "x": 110, "y": 148,
                "text": "✓ Coffee Board Registered Planter",
                "props": {"fontSize": 10, "fontWeight": 700, "fill": C_EMERALD}
            }
        },

        # Bilingual Language Switcher Card
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LangCard",
                "parent": f6,
                "x": 20, "y": 198, "width": 350, "height": 64,
                "props": {"fill": C_WHITE, "cornerRadius": 18, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LangCardLabel",
                "parent": f6,
                "x": 36, "y": 218,
                "text": "App Language (ಭಾಷೆ ಆಯ್ಕೆ)",
                "props": {"fontSize": 13, "fontWeight": 600, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LangBtnKn",
                "parent": f6,
                "x": 230, "y": 210, "width": 64, "height": 38,
                "props": {"fill": C_PRIMARY, "cornerRadius": 12}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LangBtnKnText",
                "parent": f6,
                "x": 244, "y": 222,
                "text": "ಕನ್ನಡ",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": C_WHITE}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "LangBtnEn",
                "parent": f6,
                "x": 300, "y": 210, "width": 56, "height": 38,
                "props": {"fill": "#F1F5F9", "cornerRadius": 12}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "LangBtnEnText",
                "parent": f6,
                "x": 314, "y": 222,
                "text": "ENG",
                "props": {"fontSize": 12, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },

        # Estate Season Analytics (3 Tiles: Total Scans, Healthy %, Active Lots)
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "StatTile1",
                "parent": f6,
                "x": 20, "y": 274, "width": 108, "height": 72,
                "props": {"fill": C_WHITE, "cornerRadius": 16, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "StatNum1",
                "parent": f6,
                "x": 44, "y": 286,
                "text": "34",
                "props": {"fontSize": 18, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "StatLabel1",
                "parent": f6,
                "x": 32, "y": 314,
                "text": "Total Scans",
                "props": {"fontSize": 10, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },

        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "StatTile2",
                "parent": f6,
                "x": 140, "y": 274, "width": 110, "height": 72,
                "props": {"fill": C_EMERALD_BG, "cornerRadius": 16, "stroke": C_EMERALD, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "StatNum2",
                "parent": f6,
                "x": 172, "y": 286,
                "text": "88%",
                "props": {"fontSize": 18, "fontWeight": 700, "fill": C_EMERALD}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "StatLabel2",
                "parent": f6,
                "x": 154, "y": 314,
                "text": "Healthy Crop",
                "props": {"fontSize": 10, "fontWeight": 600, "fill": "#065F46"}
            }
        },

        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "StatTile3",
                "parent": f6,
                "x": 262, "y": 274, "width": 108, "height": 72,
                "props": {"fill": C_ACCENT_BG, "cornerRadius": 16, "stroke": C_ACCENT, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "StatNum3",
                "parent": f6,
                "x": 306, "y": 286,
                "text": "3",
                "props": {"fontSize": 18, "fontWeight": 700, "fill": C_ACCENT}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "StatLabel3",
                "parent": f6,
                "x": 282, "y": 314,
                "text": "Active Lots",
                "props": {"fontSize": 10, "fontWeight": 600, "fill": "#7C2D12"}
            }
        },

        # Diagnostic History Timeline Header
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistorySectionTitle",
                "parent": f6,
                "x": 24, "y": 366,
                "text": "Recent Diagnostic Field Scans",
                "props": {"fontSize": 14, "fontWeight": 700, "fill": C_TEXT_DARK}
            }
        },

        # Scan History Item 1: Rust
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "HistoryItem1",
                "parent": f6,
                "x": 20, "y": 396, "width": 350, "height": 84,
                "props": {"fill": C_WHITE, "cornerRadius": 18, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "HistoryThumb1",
                "parent": f6,
                "x": 32, "y": 408, "width": 60, "height": 60,
                "props": {"fill": "#F59E0B20", "cornerRadius": 12}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistoryThumbIcon1",
                "parent": f6,
                "x": 52, "y": 426,
                "text": "🍂",
                "props": {"fontSize": 18}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistoryItemTitle1",
                "parent": f6,
                "x": 104, "y": 408,
                "text": "Coffee Leaf Rust • 94.8%",
                "props": {"fontSize": 13, "fontWeight": 700, "fill": C_AMBER}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistoryItemDate1",
                "parent": f6,
                "x": 104, "y": 428,
                "text": "Plot 4 (North Block) • May 24, 2026\nStatus: Bordeaux 1% spray scheduled",
                "props": {"fontSize": 10, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistoryViewAdvisory1",
                "parent": f6,
                "x": 268, "y": 438,
                "text": "View CCRI →",
                "props": {"fontSize": 11, "fontWeight": 700, "fill": C_PRIMARY}
            }
        },

        # Scan History Item 2: Healthy
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "HistoryItem2",
                "parent": f6,
                "x": 20, "y": 492, "width": 350, "height": 84,
                "props": {"fill": C_WHITE, "cornerRadius": 18, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "HistoryThumb2",
                "parent": f6,
                "x": 32, "y": 504, "width": 60, "height": 60,
                "props": {"fill": C_EMERALD_BG, "cornerRadius": 12}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistoryThumbIcon2",
                "parent": f6,
                "x": 52, "y": 522,
                "text": "🌿",
                "props": {"fontSize": 18}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistoryItemTitle2",
                "parent": f6,
                "x": 104, "y": 504,
                "text": "Healthy Coffee Foliage • 98.2%",
                "props": {"fontSize": 13, "fontWeight": 700, "fill": C_EMERALD}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "HistoryItemDate2",
                "parent": f6,
                "x": 104, "y": 524,
                "text": "Nursery Plot 1 • May 18, 2026\nStatus: Optimal chlorophyll development",
                "props": {"fontSize": 10, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        },

        # In-App Server IP Switcher & Offline Cache Status
        {
            "command": "node.create",
            "params": {
                "type": "frame",
                "name": "NetworkSettingsCard",
                "parent": f6,
                "x": 20, "y": 596, "width": 350, "height": 76,
                "props": {"fill": "#F1F5F9", "cornerRadius": 18, "stroke": C_BORDER, "strokeWeight": 1}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "NetworkSettingsTitle",
                "parent": f6,
                "x": 36, "y": 608,
                "text": "⚙️ Backend Server IP Switcher",
                "props": {"fontSize": 12, "fontWeight": 700, "fill": C_TEXT_DARK}
            }
        },
        {
            "command": "node.create",
            "params": {
                "type": "text",
                "name": "NetworkSettingsSub",
                "parent": f6,
                "x": 36, "y": 628,
                "text": "Current Target: 192.168.1.15:8000 (● Connected, 14ms)\n14 CCRI Agronomy Manuals Cached for Offline Field Diagnostics",
                "props": {"fontSize": 10, "fontWeight": 500, "fill": C_TEXT_MUTED}
            }
        }
    ])

    print(f"[*] Adding {len(all_child_commands)} UI elements across 6 mobile screens...")
    child_results = run_commands(all_child_commands, in_file=FIGCRAFT_FILE, out_file=FIGCRAFT_FILE)
    if child_results:
        success_count = sum(1 for r in child_results if r.get("ok"))
        print(f"[+] Successfully generated {success_count}/{len(all_child_commands)} UI elements into {FIGCRAFT_FILE}!")

    # Stage 3: Export to High-Res PNGs, SVG, and Native Figma (.fig) file
    print("[*] Exporting Mobile Screens...")

    # Export whole canvas to PNG preview
    preview_png = os.path.join(OUTPUT_DIR, "all_screens_preview.png")
    subprocess.run([FIGCRAFT_BIN, "export", FIGCRAFT_FILE, "-o", preview_png, "--scale", "2"])
    print(f"  [+] Canvas Preview PNG: {preview_png}")

    # Export to native Figma (.fig) format
    figma_fig = os.path.join(OUTPUT_DIR, "plantiq_mobile_v2.fig")
    subprocess.run([FIGCRAFT_BIN, "export", FIGCRAFT_FILE, "-o", figma_fig, "--format", "fig"])
    print(f"  [+] Native Figma (.fig) File: {figma_fig}")

    # Export each screen individually to PNG
    for s in screens:
        screen_png = os.path.join(OUTPUT_DIR, f"{s['name']}.png")
        subprocess.run([
            FIGCRAFT_BIN, "export", FIGCRAFT_FILE,
            "-o", screen_png,
            "--node", str(s_map[s["name"]]),
            "--scale", "2"
        ])
        print(f"  [+] Screen Render: {screen_png}")

    print("\n[SUCCESS] All 6 Mobile Screens Generated and Exported to figma-design/!")


if __name__ == "__main__":
    build_all_screens()
