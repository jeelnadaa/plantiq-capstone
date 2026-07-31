import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import torch.nn.functional as F
from PIL import Image

CLASSES = ["Miner", "Rust", "Phoma", "Healthy", "Cerscospora"]

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_model(weights_path='best_resnet50_coffee.pth'):
    """Initializes and returns the ResNet50 model loaded with weights."""
    print("Loading model...")
    model = models.resnet50(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.4), 
        nn.Linear(num_features, 5) 
    )
    
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location=device))
        print("Model weights loaded successfully.")
    else:
        print(f"Warning: Model weights not found at {weights_path}. Using uninitialized weights.")
        
    model = model.to(device)
    model.eval()
    return model

# Transformation for incoming uploaded web images
inference_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def predict_image(model, image_bytes):
    """Predicts the class and confidence for a raw image byte stream."""
    try:
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes)).convert('RGB')
        tensor = inference_transform(img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = F.softmax(outputs, dim=1)[0]
            confidence, predicted_idx = torch.max(probabilities, 0)
            
        return {
            "class": CLASSES[predicted_idx.item()],
            "confidence": float(confidence.item() * 100),
            "distribution": {CLASSES[i]: float(probabilities[i].item() * 100) for i in range(len(CLASSES))}
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {"error": str(e)}

class CoffeeNpyDataset(Dataset):
    """Dataset for the evaluation of .npy files"""
    def __init__(self, X_path, y_path):
        self.X = np.load(X_path)
        self.y = np.load(y_path)
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        image = self.X[idx] 
        label = self.y[idx]
        if self.transform:
            image = self.transform(image)
        label = torch.tensor(label, dtype=torch.long)
        return image, label

def evaluate_npy_dataset(model, npy_dir, task_num=1, batch_size=32):
    """Evaluates the test/val datasets directly from the directory."""
    X_test_path = os.path.join(npy_dir, f"task{task_num}_X_test.npy")
    y_test_path = os.path.join(npy_dir, f"task{task_num}_y_test.npy")
    
    if not os.path.exists(X_test_path) or not os.path.exists(y_test_path):
        return {"error": f"Required test .npy files not found in {npy_dir}"}
        
    dataset = CoffeeNpyDataset(X_test_path, y_test_path)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    
    all_preds = []
    all_labels = []
    
    print("Starting bulk evaluation...")
    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    # Calculate metrics
    report = classification_report(all_labels, all_preds, target_names=CLASSES, output_dict=True, zero_division=0)
    cm = confusion_matrix(all_labels, all_preds).tolist() # Convert to standard list for JSON
    accuracy = accuracy_score(all_labels, all_preds)
    
    return {
        "accuracy": accuracy * 100,
        "macro_f1": report["macro avg"]["f1-score"],
        "macro_precision": report["macro avg"]["precision"],
        "macro_recall": report["macro avg"]["recall"],
        "class_metrics": {c: report[c] for c in CLASSES},
        "confusion_matrix": cm,
        "classes": CLASSES
    }
