import os
import time
from io import BytesIO
from typing import Dict, Any
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from app.core.config import settings
from app.core.terminal_logger import tracker

CLASSES = ['Miner', 'Rust', 'Phoma', 'Healthy', 'Cerscospora']
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class CNNModelWrapper:
    def __init__(self, weights_path: str = settings.CNN_WEIGHTS_PATH):
        self.weights_path = weights_path
        self.model = self._load_model()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_model(self) -> nn.Module:
        model = models.resnet50(weights=None)
        num_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(num_features, len(CLASSES))
        )
        if os.path.exists(self.weights_path):
            try:
                # Security hardening: weights_only=True prevents arbitrary pickle code execution
                state_dict = torch.load(self.weights_path, map_location=device, weights_only=True)
                model.load_state_dict(state_dict)
                print(f'[Cleaned CNN] Loaded weights safely (weights_only=True) from {self.weights_path}')
            except Exception as e:
                print(f'[Cleaned CNN] Error loading weights: {e}')
        else:
            print(f'[Cleaned CNN] Warning: weights path not found: {self.weights_path}')
        model = model.to(device)
        model.eval()
        return model

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        t0 = time.perf_counter()
        tracker.log_cnn_start(str(device))
        try:
            # 1. Preprocess
            t_prep_0 = time.perf_counter()
            img = Image.open(BytesIO(image_bytes)).convert('RGB')
            tensor = self.transform(img).unsqueeze(0).to(device)
            t_prep = (time.perf_counter() - t_prep_0) * 1000.0
            tracker.log_cnn_step(1, 3, f"Image preprocessing (Resize 224x224, Normalize) -> Tensor on {device.type.upper()}", t_prep)

            # 2. Forward pass
            t_fwd_0 = time.perf_counter()
            with torch.no_grad():
                outputs = self.model(tensor)
                t_fwd = (time.perf_counter() - t_fwd_0) * 1000.0
                tracker.log_cnn_step(2, 3, f"ResNet-50 Forward Pass on {device.type.upper()}", t_fwd)

                # 3. Softmax & probability extraction
                probabilities = F.softmax(outputs, dim=1)[0]
                confidence, predicted_idx = torch.max(probabilities, 0)
            
            predicted_class = CLASSES[predicted_idx.item()]
            conf_percent = float(confidence.item() * 100.0)
            distribution = {CLASSES[i]: float(probabilities[i].item() * 100.0) for i in range(len(CLASSES))}
            
            total_ms = (time.perf_counter() - t0) * 1000.0
            tracker.log_cnn_step(3, 3, f"Softmax probability & argmax class extraction")
            tracker.log_cnn_result(predicted_class, conf_percent, distribution, total_ms)

            return {
                'class': predicted_class,
                'confidence': conf_percent,
                'distribution': distribution
            }
        except Exception as e:
            print(f"[CNN Service] Inference error: {e}")
            return {'error': str(e), 'class': 'Unknown', 'confidence': 0.0, 'distribution': {}}

_cnn_instance = None
def get_detector() -> CNNModelWrapper:
    global _cnn_instance
    if _cnn_instance is None:
        _cnn_instance = CNNModelWrapper()
    return _cnn_instance
