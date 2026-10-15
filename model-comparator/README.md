# 🌿 PlantIQ — Dual CNN Model Comparator & Benchmark Suite

An isolated, interactive side-by-side comparison web application designed to evaluate the **exact same coffee leaf image** across two distinct deep learning architectures:
1. **Model A (Old Model)**: **PyTorch ResNet-50** (`cnn/best_resnet50_coffee.pth`)
2. **Model B (New Model)**: **Custom 4-Block Keras CNN** (`new-cnn/coffee_leaf_cnn_final.keras`)

---

## 📊 Side-by-Side Model Specifications

| Evaluation Dimension | Model A: Old Model (PyTorch ResNet-50) | Model B: New Model (Custom Keras CNN) |
| :--- | :--- | :--- |
| **Benchmark Test Accuracy** | **96.40%** | **89.19%** |
| **Benchmark Precision** | **96.80%** | **90.86%** |
| **Benchmark Recall** | **96.10%** | **85.95%** |
| **Architecture Type** | Deep Residual Learning (50 Layers) with Bottlenecks | Custom 4-Stage Conv2D + L2 Regularization |
| **Parameter Count** | **25,557,029** (~25.5 Million) | **3,712,421** (~3.71 Million) |
| **Input Shape** | `(3, 224, 224)` with ImageNet Normalization | `(224, 224, 3)` with MinMax Rescaling (`/255.0`) |
| **Weights File** | `best_resnet50_coffee.pth` | `coffee_leaf_cnn_final.keras` |
| **Target Dataset** | JMuBEN + Field Verified Datasets | JMuBEN (Deduplicated with MD5 & pHash) |

---

## 🚀 How to Run the Web Application

### Step 1: Open Terminal & Navigate to Directory
```bash
cd d:\end-capstone-project\model-comparator
```

### Step 2: Install Requirements (If not already installed)
```bash
pip install -r requirements.txt
```
*(Dependencies: `fastapi`, `uvicorn`, `torch`, `torchvision`, `pillow`, `numpy`, `h5py`)*

### Step 3: Start the Comparator App
```bash
python run_app.py
```
*Or simply double-click **`run.bat`** on Windows.*

### Step 4: Open in Browser
The app starts automatically on:
👉 **`http://localhost:8501`** (or `http://127.0.0.1:8501`)

---

## 🔬 How to Use the Application

1. **Upload Custom Leaves**:
   * Drag and drop any coffee leaf photo from your phone, field camera, or desktop into the dropzone.
2. **1-Click Preset Ground-Truth Samples**:
   * Click on any of the 5 preset sample cards (*Coffee Leaf Rust*, *Cercospora*, *Leaf Miner*, *Phoma Blight*, *Healthy Leaf*) to run an instant dual comparison.
3. **Analyze Side-by-Side Results**:
   * **Predicted Disease Class**: View diagnoses side by side.
   * **Live Confidence (%)**: Compare live Softmax probabilities and animated progress gauges.
   * **Published Benchmark Accuracies**: Displays reported test-set accuracy (**96.40%** for ResNet-50 vs **89.19%** for Custom CNN).
   * **Inference Latency**: Measures forward-pass execution time in milliseconds (ms).
   * **5-Class Softmax Distribution Table**: Detailed row-by-row percentage breakdown across all 5 classes with delta indicators ($+$ / $-$).
   * **Consensus Diagnostics Banner**: Highlights whether both models firmly agree (🟢 *Full Model Consensus*) or identify conflicting symptoms (🟡 *Diagnostic Divergence*).

---

## 📁 Directory Structure

```
d:\end-capstone-project\model-comparator\
├── backend\
│   ├── app.py                      # FastAPI server & endpoints (/api/compare, /api/samples)
│   └── dual_model_service.py       # DualModelComparator engine (PyTorch ResNet-50 + Custom CNN)
├── static\
│   ├── css\
│   │   └── style.css               # Modern glassmorphic agronomy UI stylesheet
│   └── js\
│       └── app.js                  # Client controller, drag-and-drop, dynamic chart rendering
├── templates\
│   ├── index.html                  # Responsive side-by-side comparison dashboard
├── sample_images\                  # Preset ground-truth test leaves for 1-click evaluation
│   ├── rust_sample.jpg
│   ├── cercospora_sample.jpg
│   ├── miner_sample.jpg
│   ├── phoma_sample.jpg
│   └── healthy_sample.jpg
├── requirements.txt                # Self-contained dependency list
├── run_app.py                      # Standalone Python launcher
├── run.bat                         # Windows 1-click batch launcher
└── README.md                       # Comprehensive User Guide & Architecture Documentation
```

---

## 🎓 Key Academic Insights for Evaluators & Professors

1. **Why does ResNet-50 achieve higher accuracy (96.40% vs 89.19%)?**
   * ResNet-50 utilizes **$1\times1 \to 3\times3 \to 1\times1$ residual bottleneck blocks** with identity skip connections, allowing it to preserve subtle microscopic pustule textures across 50 layers without vanishing gradients.
2. **When is the Custom 4-Block CNN advantageous?**
   * The custom CNN has only **3.71M parameters** (vs. 25.5M in ResNet-50), making it **$\sim 7\times$ lighter** in memory footprint, suitable for ultra-low-cost microcontrollers or edge devices with strict RAM limits.
3. **Zero Impact on Existing Codebase**:
   * This application is completely standalone in `model-comparator/` and does not modify or interfere with the production `cleaned/` or `backend/` applications.
