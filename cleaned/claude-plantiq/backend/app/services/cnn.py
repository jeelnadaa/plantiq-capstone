"""ResNet-50 coffee-leaf classifier — same architecture, weights, classes and preprocessing as the original app."""
from __future__ import annotations

import io
import logging
import threading
from pathlib import Path

from app.core.config import settings

log = logging.getLogger("plantiq.cnn")

# Order matters: it is the order of the trained output layer.
CLASSES = ["Miner", "Rust", "Phoma", "Healthy", "Cerscospora"]

DISPLAY = {
    "Miner": {"en": "Coffee Leaf Miner", "kn": "ಕಾಫಿ ಎಲೆ ಸುರಂಗ ಕೀಟ", "latin": "Leucoptera coffeella", "kind": "pest"},
    "Rust": {"en": "Coffee Leaf Rust", "kn": "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ", "latin": "Hemileia vastatrix", "kind": "disease"},
    "Phoma": {"en": "Phoma Leaf Spot", "kn": "ಫೋಮಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ", "latin": "Phoma costarricensis", "kind": "disease"},
    "Healthy": {"en": "Healthy Leaf", "kn": "ಆರೋಗ್ಯಕರ ಎಲೆ", "latin": "", "kind": "healthy"},
    "Cerscospora": {"en": "Cercospora Leaf Spot", "kn": "ಸೆರ್ಕೋಸ್ಪೊರಾ ಎಲೆ ಚುಕ್ಕೆ ರೋಗ", "latin": "Cercospora coffeicola",
                    "kind": "disease"},
}


def resolve_device(pref: str | None = None) -> str:
    pref = (pref or settings.ML_DEVICE or "auto").lower()
    try:
        import torch

        if pref == "cpu":
            return "cpu"
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


class CNNClassifier:
    def __init__(self, weights_path: Path | None = None, device: str | None = None) -> None:
        import torch
        from torch import nn
        from torchvision import models, transforms

        self._torch = torch
        self.weights_path = Path(weights_path or settings.CNN_WEIGHTS_PATH)
        self.device = resolve_device(device)
        model = models.resnet50(weights=None)
        model.fc = nn.Sequential(nn.Dropout(0.4), nn.Linear(model.fc.in_features, len(CLASSES)))
        if not self.weights_path.exists():
            raise FileNotFoundError(f"CNN weights not found at {self.weights_path}")
        # weights_only=True: refuses pickled code objects (arbitrary code execution guard).
        state = torch.load(str(self.weights_path), map_location=self.device, weights_only=True)
        model.load_state_dict(state)
        self.model = model.to(self.device).eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self._lock = threading.Lock()
        log.info("CNN loaded from %s on %s", self.weights_path.name, self.device)

    def predict(self, image_bytes: bytes) -> dict:
        from PIL import Image

        torch = self._torch
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        with self._lock, torch.inference_mode():
            probs = torch.softmax(self.model(tensor), dim=1)[0].float().cpu()
        conf, idx = torch.max(probs, 0)
        return {
            "class": CLASSES[int(idx)],
            "confidence": round(float(conf) * 100.0, 2),
            "distribution": {c: round(float(probs[i]) * 100.0, 2) for i, c in enumerate(CLASSES)},
        }


def display_name(cls: str, lang: str = "en") -> str:
    d = DISPLAY.get(cls)
    return d.get(lang, d["en"]) if d else cls
