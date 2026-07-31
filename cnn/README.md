# PlantIQ: Coffee Leaf Disease Inference

PlantIQ is a web application designed to detect diseases in coffee leaves using deeply learned Computer Vision. The application features a modern, Apple-inspired minimalist UI built on top of a highly optimized PyTorch backend, capable of processing both single image inference batches and bulk dataset evaluation tests.

## Model Details

The brain behind the application is a **ResNet50** Convolutional Neural Network (CNN).
- **Architecture**: A pre-trained ResNet50 backbone (IMAGENET1K_V1) where the dense classification head was replaced to narrow down predictions.
- **Custom Head**: A sequential set of layers including a `Dropout(0.4)` and a `Linear(in_features, 5)` mapping layer. The feature extraction layers are frozen during evaluation.
- **Classes Supported**:
  1. Miner
  2. Rust
  3. Phoma
  4. Healthy
  5. Cerscospora

## Dataset Evaluation
A unique feature of this project is the onboard dataset evaluator. Using strict pre-processed NumPy arrays (`task1_X_test.npy` & `task1_y_test.npy`), the application can run inferences over thousands of validation arrays right from the browser. It computes the absolute True vs Predicted matches to calculate overall **Accuracy, Macro F1-Score, Precision, and Recall**.

## Tech Stack
- **Backend Framework**: Flask (Python)
- **Deep Learning Library**: PyTorch & Torchvision
- **Frontend Design**: Vanilla HTML/CSS/JS (Satoshi Font, Custom "Apple" aesthetic)
- **Metrics**: Scikit-Learn
- **Data Handling**: NumPy, Pillow
- **Charts**: Chart.js

---

## How to Run the Project

### Prerequisites
Make sure you have Python 3.8+ installed. It is highly recommended to use a virtual environment.

### 1. Install Dependencies
First, install the standard web and data libraries:

```bash
pip install -r requirements.txt
```

Then, install PyTorch, Torchvision, and Torchaudio explicitly compiled for **CUDA 11.8**:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

### 2. Prepare the Data
Ensure that you have the model weights and data inside the project directory:
- `best_resnet50_coffee.pth` (The pre-trained model weights)
- `task1_X_test.npy` & `task1_y_test.npy` (Used for the dataset evaluation UI)
*(Note: These files must be located in the root inference directory alongside `app.py`)*

### 3. Start the Server
Start the Flask application by running:

```bash
python app.py
```

### 4. Open in Browser
Open Google Chrome and navigate to:
```
http://localhost:5000
```
Drag and drop images to see live predictions, or head down to the bottom of the page to run the bulk dataset test.
