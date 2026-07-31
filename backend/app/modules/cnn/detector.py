import os
from io import BytesIO
from typing import Dict, Any
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from app.core.config import settings

CLASSES = ["Miner", "Rust", "Phoma", "Healthy", "Cerscospora"]
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
        print(f"[CNN] Loading ResNet50 model with device={device}...")
        model = models.resnet50(weights=None)
        num_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(num_features, len(CLASSES))
        )
        
        if os.path.exists(self.weights_path):
            try:
                state_dict = torch.load(self.weights_path, map_location=device)
                model.load_state_dict(state_dict)
                print(f"[CNN] Successfully loaded weights from {self.weights_path}")
            except Exception as e:
                print(f"[CNN] Error loading weights from {self.weights_path}: {e}")
        else:
            print(f"[CNN] Warning: Weights file not found at {self.weights_path}. Using uninitialized weights.")

        model = model.to(device)
        model.eval()
        return model

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """Runs ResNet50 inference on image bytes."""
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
            tensor = self.transform(img).unsqueeze(0).to(device)

            with torch.no_grad():
                outputs = self.model(tensor)
                probabilities = F.softmax(outputs, dim=1)[0]
                confidence, predicted_idx = torch.max(probabilities, 0)

            predicted_class = CLASSES[predicted_idx.item()]
            conf_percent = float(confidence.item() * 100.0)
            distribution = {CLASSES[i]: float(probabilities[i].item() * 100.0) for i in range(len(CLASSES))}

            return {
                "class": predicted_class,
                "confidence": round(conf_percent, 2),
                "is_healthy": predicted_class == "Healthy",
                "distribution": distribution,
                "error": None
            }
        except Exception as e:
            print(f"[CNN] Prediction Error: {e}")
            return {
                "class": "Unknown",
                "confidence": 0.0,
                "is_healthy": False,
                "distribution": {},
                "error": str(e)
            }

# Singleton instance
_detector_instance = None

def get_detector() -> CNNModelWrapper:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = CNNModelWrapper()
    return _detector_instance
