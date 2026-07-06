import logging
from pathlib import Path

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

from src.cv.model import PlantDiseaseResNet

logger = logging.getLogger(__name__)

CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy",
]

MODEL_PATH = Path(__file__).resolve().parent.parent / "api" / "model" / "best_model.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model

    model = PlantDiseaseResNet(num_classes=len(CLASSES))
    state_dict = torch.load(str(MODEL_PATH), map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    _model = model
    logger.info("Model loaded successfully on %s", device)
    return _model


def preprocess_image(image: Image.Image) -> torch.Tensor:
    image = image.convert("RGB")
    tensor = _transform(image).unsqueeze(0).to(device)
    return tensor


@torch.no_grad()
def predict(image: Image.Image, top_k: int = 5):
    model = _load_model()
    tensor = preprocess_image(image)
    output = model(tensor)[0]
    probs = F.softmax(output, dim=0).cpu().numpy()
    top_indices = probs.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "class_name": CLASSES[idx],
            "confidence": round(float(probs[idx]) * 100, 2),
        })

    return {
        "predictions": results,
        "top_class": results[0]["class_name"],
        "top_confidence": results[0]["confidence"],
    }
