"""
dual_model_service.py
=====================
Dual CNN Inference & Model Comparison Engine for PlantIQ.

Compares:
- Model A: Old PyTorch ResNet-50 (Transfer Learning on Deep Residual Bottlenecks)
  * Benchmark Test Accuracy: 96.40%
  * Parameter Count: ~25.5 Million
  * Weights: best_resnet50_coffee.pth

- Model B: New Custom 4-Block Conv2D (Custom Architecture trained on JMuBEN)
  * Benchmark Test Accuracy: 89.19%
  * Parameter Count: ~3.7 Million
  * Weights: coffee_leaf_cnn_final.keras
"""

import os
import time
from io import BytesIO
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image
import h5py
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms

# Paths configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)

OLD_WEIGHTS_CANDIDATES = [
    os.path.join(ROOT_DIR, "cleaned", "backend", "app", "services", "best_resnet50_coffee.pth"),
    os.path.join(ROOT_DIR, "cnn", "best_resnet50_coffee.pth"),
    os.path.join(ROOT_DIR, "backend", "app", "modules", "cnn", "resnet50_coffee_leaf_model.pth")
]

NEW_WEIGHTS_PATH = os.path.join(ROOT_DIR, "new-cnn", "coffee_leaf_cnn_final.keras")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Canonical 5 Classes for unified presentation
CANONICAL_CLASSES = [
    "Cercospora Leaf Spot",
    "Coffee Leaf Rust",
    "Coffee Leaf Miner",
    "Phoma Blight",
    "Healthy Leaf"
]

# Raw class mapping for Old Model: ['Miner', 'Rust', 'Phoma', 'Healthy', 'Cerscospora']
OLD_RAW_CLASSES = ['Miner', 'Rust', 'Phoma', 'Healthy', 'Cerscospora']
OLD_TO_CANONICAL_MAP = {
    'Cerscospora': 'Cercospora Leaf Spot',
    'Rust': 'Coffee Leaf Rust',
    'Miner': 'Coffee Leaf Miner',
    'Phoma': 'Phoma Blight',
    'Healthy': 'Healthy Leaf'
}

# Raw class mapping for New Model: ['Cercospora', 'Healthy', 'Miner', 'Phoma', 'Rust']
NEW_RAW_CLASSES = ['Cercospora', 'Healthy', 'Miner', 'Phoma', 'Rust']
NEW_TO_CANONICAL_MAP = {
    'Cercospora': 'Cercospora Leaf Spot',
    'Rust': 'Coffee Leaf Rust',
    'Miner': 'Coffee Leaf Miner',
    'Phoma': 'Phoma Blight',
    'Healthy': 'Healthy Leaf'
}


class CustomCoffeeLeafCNN(nn.Module):
    """
    Exact PyTorch implementation of the 4-Stage Conv2D Keras architecture 
    from 'new-cnn/coffee_leaf_disease_CNN_JMuBEN (1).ipynb'.
    Allows 100% mathematical fidelity execution with zero TensorFlow/Protobuf version conflicts.
    """
    def __init__(self, num_classes: int = 5):
        super().__init__()
        def conv_block(in_c, out_c, p_drop):
            return nn.ModuleDict({
                'conv1': nn.Conv2d(in_c, out_c, 3, padding=1),
                'bn1': nn.BatchNorm2d(out_c),
                'conv2': nn.Conv2d(out_c, out_c, 3, padding=1),
                'bn2': nn.BatchNorm2d(out_c),
                'pool': nn.MaxPool2d(2, 2),
                'drop': nn.Dropout(p_drop)
            })
        
        self.b1 = conv_block(3, 32, 0.20)
        self.b2 = conv_block(32, 64, 0.25)
        self.b3 = conv_block(64, 128, 0.30)
        self.b4 = conv_block(128, 256, 0.35)
        
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc1 = nn.Linear(256, 256)
        self.bn_fc = nn.BatchNorm1d(256)
        self.drop_fc = nn.Dropout(0.5)
        self.out = nn.Linear(256, num_classes)

    def forward(self, x):
        for b in [self.b1, self.b2, self.b3, self.b4]:
            x = F.relu(b['bn1'](b['conv1'](x)))
            x = F.relu(b['bn2'](b['conv2'](x)))
            x = b['drop'](b['pool'](x))
        x = self.gap(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.bn_fc(self.fc1(x)))
        x = self.drop_fc(x)
        x = self.out(x)
        return x


class DualModelComparator:
    def __init__(self):
        self.old_model: Optional[nn.Module] = None
        self.new_model: Optional[nn.Module] = None
        self.old_weights_path = self._find_old_weights()
        self.new_weights_path = NEW_WEIGHTS_PATH
        
        # Preprocessing transforms
        self.old_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        self.new_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor() # Scaled to [0, 1] as in notebook (img_to_array / 255.0)
        ])

        self._load_models()

    def _find_old_weights(self) -> str:
        for p in OLD_WEIGHTS_CANDIDATES:
            if os.path.exists(p):
                return p
        return OLD_WEIGHTS_CANDIDATES[0]

    def _load_models(self):
        # 1. Load Old PyTorch ResNet-50
        print(f"[Model Comparator] Initializing Old ResNet-50 Model from: {self.old_weights_path}")
        try:
            m_old = models.resnet50(weights=None)
            num_features = m_old.fc.in_features
            m_old.fc = nn.Sequential(
                nn.Dropout(0.4),
                nn.Linear(num_features, len(OLD_RAW_CLASSES))
            )
            if os.path.exists(self.old_weights_path):
                state = torch.load(self.old_weights_path, map_location=device)
                m_old.load_state_dict(state)
                print("  [+] Old ResNet-50 weights loaded successfully.")
            else:
                print(f"  [!] Warning: Old weights not found at {self.old_weights_path}")
            m_old = m_old.to(device)
            m_old.eval()
            self.old_model = m_old
        except Exception as e:
            print(f"  [-] Error initializing Old ResNet-50: {e}")

        # 2. Load New Custom Keras/PyTorch CNN
        print(f"[Model Comparator] Initializing New Custom CNN Model from: {self.new_weights_path}")
        try:
            m_new = CustomCoffeeLeafCNN(num_classes=5)
            if os.path.exists(self.new_weights_path):
                self._load_keras_h5_weights(m_new, self.new_weights_path)
                print("  [+] New Custom CNN weights loaded successfully from HDF5.")
            else:
                print(f"  [!] Warning: New weights not found at {self.new_weights_path}")
            m_new = m_new.to(device)
            m_new.eval()
            self.new_model = m_new
        except Exception as e:
            print(f"  [-] Error initializing New Custom CNN: {e}")

    def _load_keras_h5_weights(self, model: CustomCoffeeLeafCNN, h5_path: str):
        with h5py.File(h5_path, 'r') as f:
            w_grp = f['model_weights']
            
            def load_conv(conv_layer, name):
                g = w_grp[name]
                k = g['kernel:0'][:] if 'kernel:0' in g else g[f'{name}/kernel:0'][:]
                b = g['bias:0'][:] if 'bias:0' in g else g[f'{name}/bias:0'][:]
                conv_layer.weight.data = torch.from_numpy(np.transpose(k, (3, 2, 0, 1))).float()
                conv_layer.bias.data = torch.from_numpy(b).float()

            def load_bn(bn_layer, name):
                g = w_grp[name]
                gamma = g['gamma:0'][:] if 'gamma:0' in g else g[f'{name}/gamma:0'][:]
                beta = g['beta:0'][:] if 'beta:0' in g else g[f'{name}/beta:0'][:]
                mean = g['moving_mean:0'][:] if 'moving_mean:0' in g else g[f'{name}/moving_mean:0'][:]
                var = g['moving_variance:0'][:] if 'moving_variance:0' in g else g[f'{name}/moving_variance:0'][:]
                bn_layer.weight.data = torch.from_numpy(gamma).float()
                bn_layer.bias.data = torch.from_numpy(beta).float()
                bn_layer.running_mean.data = torch.from_numpy(mean).float()
                bn_layer.running_var.data = torch.from_numpy(var).float()

            def load_dense(dense_layer, name):
                g = w_grp[name]
                k = g['kernel:0'][:] if 'kernel:0' in g else g[f'{name}/kernel:0'][:]
                b = g['bias:0'][:] if 'bias:0' in g else g[f'{name}/bias:0'][:]
                dense_layer.weight.data = torch.from_numpy(k.T).float()
                dense_layer.bias.data = torch.from_numpy(b).float()

            load_conv(model.b1['conv1'], 'conv2d')
            load_bn(model.b1['bn1'], 'batch_normalization')
            load_conv(model.b1['conv2'], 'conv2d_1')
            load_bn(model.b1['bn2'], 'batch_normalization_1')

            load_conv(model.b2['conv1'], 'conv2d_2')
            load_bn(model.b2['bn1'], 'batch_normalization_2')
            load_conv(model.b2['conv2'], 'conv2d_3')
            load_bn(model.b2['bn2'], 'batch_normalization_3')

            load_conv(model.b3['conv1'], 'conv2d_4')
            load_bn(model.b3['bn1'], 'batch_normalization_4')
            load_conv(model.b3['conv2'], 'conv2d_5')
            load_bn(model.b3['bn2'], 'batch_normalization_5')

            load_conv(model.b4['conv1'], 'conv2d_6')
            load_bn(model.b4['bn1'], 'batch_normalization_6')
            load_conv(model.b4['conv2'], 'conv2d_7')
            load_bn(model.b4['bn2'], 'batch_normalization_7')

            load_dense(model.fc1, 'dense')
            load_bn(model.bn_fc, 'batch_normalization_8')
            load_dense(model.out, 'dense_1')

    def predict_dual(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Executes parallel inference across both models on the exact same leaf image.
        Returns detailed side-by-side metrics and comparison analysis.
        """
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            return {"error": f"Invalid image format: {e}"}

        # ----------------------------------------------------
        # 1. INFERENCE ON MODEL A: Old PyTorch ResNet-50
        # ----------------------------------------------------
        old_pred_class = "Unknown"
        old_confidence = 0.0
        old_dist = {}
        old_latency_ms = 0.0

        if self.old_model:
            try:
                t0 = time.time()
                tensor_old = self.old_transform(img).unsqueeze(0).to(device)
                with torch.no_grad():
                    logits_old = self.old_model(tensor_old)
                    probs_old = F.softmax(logits_old, dim=1)[0].cpu().numpy()
                old_latency_ms = (time.time() - t0) * 1000.0

                top_idx_old = int(np.argmax(probs_old))
                raw_cls_old = OLD_RAW_CLASSES[top_idx_old]
                old_pred_class = OLD_TO_CANONICAL_MAP.get(raw_cls_old, raw_cls_old)
                old_confidence = float(probs_old[top_idx_old] * 100.0)

                for idx, raw_c in enumerate(OLD_RAW_CLASSES):
                    canonical_name = OLD_TO_CANONICAL_MAP.get(raw_c, raw_c)
                    old_dist[canonical_name] = float(probs_old[idx] * 100.0)
            except Exception as e:
                print(f"[Old Model] Inference error: {e}")

        # ----------------------------------------------------
        # 2. INFERENCE ON MODEL B: New Custom CNN (Keras)
        # ----------------------------------------------------
        new_pred_class = "Unknown"
        new_confidence = 0.0
        new_dist = {}
        new_latency_ms = 0.0

        if self.new_model:
            try:
                t0 = time.time()
                tensor_new = self.new_transform(img).unsqueeze(0).to(device)
                with torch.no_grad():
                    logits_new = self.new_model(tensor_new)
                    probs_new = F.softmax(logits_new, dim=1)[0].cpu().numpy()
                new_latency_ms = (time.time() - t0) * 1000.0

                top_idx_new = int(np.argmax(probs_new))
                raw_cls_new = NEW_RAW_CLASSES[top_idx_new]
                new_pred_class = NEW_TO_CANONICAL_MAP.get(raw_cls_new, raw_cls_new)
                new_confidence = float(probs_new[top_idx_new] * 100.0)

                for idx, raw_c in enumerate(NEW_RAW_CLASSES):
                    canonical_name = NEW_TO_CANONICAL_MAP.get(raw_c, raw_c)
                    new_dist[canonical_name] = float(probs_new[idx] * 100.0)
            except Exception as e:
                print(f"[New Model] Inference error: {e}")

        # ----------------------------------------------------
        # 3. COMPARATIVE ANALYSIS & CONSENSUS DIAGNOSTICS
        # ----------------------------------------------------
        is_consensus = (old_pred_class == new_pred_class)
        conf_diff = abs(old_confidence - new_confidence)

        if is_consensus:
            if conf_diff < 10.0:
                agreement_status = "Full Model Consensus"
                agreement_badge = "consensus_high"
                analysis_text = f"Both architectures firmly agree on '{old_pred_class}' with strong probability alignment (Old: {old_confidence:.1f}%, New: {new_confidence:.1f}%)."
            else:
                agreement_status = "Consensus with Confidence Shift"
                agreement_badge = "consensus_moderate"
                higher_model = "Old ResNet-50" if old_confidence > new_confidence else "New Custom CNN"
                analysis_text = f"Both models predict '{old_pred_class}', but {higher_model} exhibits notably higher certainty ({max(old_confidence, new_confidence):.1f}% vs {min(old_confidence, new_confidence):.1f}%)."
        else:
            agreement_status = "Diagnostic Divergence"
            agreement_badge = "divergence"
            analysis_text = f"Model Divergence detected: Old ResNet-50 diagnosed '{old_pred_class}' ({old_confidence:.1f}%), while New Custom CNN diagnosed '{new_pred_class}' ({new_confidence:.1f}%)."

        # Unified Class Breakdown Comparison
        distribution_comparison = []
        for c in CANONICAL_CLASSES:
            distribution_comparison.append({
                "class_name": c,
                "old_prob": round(old_dist.get(c, 0.0), 2),
                "new_prob": round(new_dist.get(c, 0.0), 2),
                "diff": round(new_dist.get(c, 0.0) - old_dist.get(c, 0.0), 2)
            })

        return {
            "success": True,
            "models": {
                "old_model": {
                    "name": "Old Model: ResNet-50 (PyTorch)",
                    "architecture": "Deep Residual Network (50 Layers) with Bottlenecks",
                    "parameters": "25.5 Million",
                    "benchmark_test_accuracy": "96.40%",
                    "predicted_class": old_pred_class,
                    "confidence": round(old_confidence, 2),
                    "latency_ms": round(old_latency_ms, 1),
                    "distribution": old_dist,
                    "weights_source": os.path.basename(self.old_weights_path)
                },
                "new_model": {
                    "name": "New Model: Custom 4-Block CNN (Keras)",
                    "architecture": "Custom 4-Stage Conv2D + L2 Reg + Dropout + GAP",
                    "parameters": "3.71 Million",
                    "benchmark_test_accuracy": "89.19%",
                    "benchmark_precision": "90.86%",
                    "benchmark_recall": "85.95%",
                    "predicted_class": new_pred_class,
                    "confidence": round(new_confidence, 2),
                    "latency_ms": round(new_latency_ms, 1),
                    "distribution": new_dist,
                    "weights_source": os.path.basename(self.new_weights_path)
                }
            },
            "comparison": {
                "is_consensus": is_consensus,
                "agreement_status": agreement_status,
                "agreement_badge": agreement_badge,
                "confidence_difference": round(conf_diff, 2),
                "analysis": analysis_text,
                "distribution_comparison": distribution_comparison
            }
        }


_comparator_instance = None

def get_model_comparator() -> DualModelComparator:
    global _comparator_instance
    if _comparator_instance is None:
        _comparator_instance = DualModelComparator()
    return _comparator_instance
