"""SNAPSHOT of backend/app/services/cnn.py (see ../SNAPSHOT.md): same architecture, weights file, classes,
preprocessing and output format; settings lookup replaced by an explicit weights path."""
from __future__ import annotations

import io
from pathlib import Path

CLASSES = ["Miner", "Rust", "Phoma", "Healthy", "Cerscospora"]

DISPLAY = {
    "Miner": {"en": "Coffee Leaf Miner", "kn": "ಕಾಫಿ ಎಲೆ ಸುರಂಗ ಕೀಟ", "latin": "Leucoptera coffeella", "kind": "pest"},
    "Rust": {"en": "Coffee Leaf Rust", "kn": "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ", "latin": "Hemileia vastatrix", "kind": "disease"},
    "Phoma": {"en": "Phoma Leaf Spot", "kn": "ಫೋಮಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ", "latin": "Phoma costarricensis", "kind": "disease"},
    "Healthy": {"en": "Healthy Leaf", "kn": "ಆರೋಗ್ಯಕರ ಎಲೆ", "latin": "", "kind": "healthy"},
    "Cerscospora": {"en": "Cercospora Leaf Spot", "kn": "ಸೆರ್ಕೋಸ್ಪೊರಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ", "latin": "Cercospora coffeicola",
                    "kind": "disease"},
}


def display_name(cls: str, lang: str = "en") -> str:
    d = DISPLAY.get(cls)
    return d.get(lang, d["en"]) if d else cls


class CoffeeCNN:
    def __init__(self, weights_path: Path, device: str = "cuda") -> None:
        import torch
        import torch.nn as nn
        from torchvision import models, transforms

        self._torch = torch
        self.device = device
        model = models.resnet50(weights=None)
        model.fc = nn.Sequential(nn.Dropout(0.4), nn.Linear(model.fc.in_features, len(CLASSES)))
        state = torch.load(str(weights_path), map_location=device, weights_only=True)
        model.load_state_dict(state)
        self.model = model.to(device).eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def predict(self, image_bytes: bytes) -> dict:
        from PIL import Image

        torch = self._torch
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            probs = torch.softmax(self.model(tensor), dim=1)[0].float().cpu()
        conf, idx = torch.max(probs, 0)
        return {
            "class": CLASSES[int(idx)],
            "confidence": round(float(conf) * 100.0, 2),
            "distribution": {c: round(float(probs[i]) * 100.0, 2) for i, c in enumerate(CLASSES)},
        }
