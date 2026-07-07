"""Computer vision module for plant-disease detection."""

from src.cv.classifier import PlantDiseaseClassifier, get_classifier
from src.cv.constants import PLANT_DISEASE_CLASSES
from src.cv.model import PlantDiseaseResNet
from src.cv.predict import predict

__all__ = [
    "PlantDiseaseClassifier",
    "PlantDiseaseResNet",
    "PLANT_DISEASE_CLASSES",
    "get_classifier",
    "predict",
]
