"""Plant-disease classifier wrapping the ResNet50 CV model."""

import logging
from pathlib import Path
from typing import Callable, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from src.config import settings
from src.cv.constants import PLANT_DISEASE_CLASSES
from src.cv.model import PlantDiseaseResNet

logger = logging.getLogger(__name__)


def _resolve_device(device: str) -> torch.device:
    """Resolve the torch device from a settings string."""
    if device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device)


def _build_model_for_checkpoint(state_dict: dict, num_classes: int) -> nn.Module:
    """
    Build a model architecture matching the checkpoint's key prefix.

    The production checkpoint uses a plain ``resnet50`` with a single
    ``nn.Linear`` classifier.  The training script uses ``PlantDiseaseResNet``
    which wraps the base model and adds a deeper head.  We detect the format
    from the state-dict keys so inference works for both.
    """
    if any(k.startswith("base_model.") for k in state_dict.keys()):
        logger.info("Detected PlantDiseaseResNet checkpoint format")
        return PlantDiseaseResNet(num_classes=num_classes)

    logger.info("Detected plain ResNet50 checkpoint format")
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


class PlantDiseaseClassifier:
    """Load the trained ResNet50 model and run plant-disease predictions."""

    def __init__(self) -> None:
        self._cfg = settings.cv
        self._device = _resolve_device(self._cfg.device)
        self._classes = PLANT_DISEASE_CLASSES
        self._model: nn.Module | None = None

        self._transform = transforms.Compose(
            [
                transforms.Resize((self._cfg.image_size, self._cfg.image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=self._cfg.normalize_mean,
                    std=self._cfg.normalize_std,
                ),
            ]
        )

    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def num_classes(self) -> int:
        return len(self._classes)

    def _load_model(self) -> nn.Module:
        """Lazy-load the model weights."""
        if self._model is not None:
            return self._model

        model_path = Path(self._cfg.model_path)
        if not model_path.is_file():
            raise FileNotFoundError(f"CV model checkpoint not found: {model_path}")

        state_dict = torch.load(
            str(model_path),
            map_location=self._device,
            weights_only=True,
        )
        model = _build_model_for_checkpoint(state_dict, self.num_classes)

        missing, unexpected = model.load_state_dict(state_dict, strict=False)
        if missing:
            logger.warning("Missing keys when loading CV checkpoint: %s", missing)
        if unexpected:
            logger.warning("Unexpected keys when loading CV checkpoint: %s", unexpected)

        model.to(self._device)
        model.eval()

        self._model = model
        logger.info("ResNet50 model loaded successfully on %s", self._device)
        return self._model

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Convert a PIL image to a normalized model input tensor."""
        rgb_image = image.convert("RGB")
        return self._transform(rgb_image).unsqueeze(0).to(self._device)

    def _tta_transforms(self) -> List[Callable[[Image.Image], torch.Tensor]]:
        """Return deterministic transforms for test-time augmentation."""
        size = self._cfg.image_size
        mean = self._cfg.normalize_mean
        std = self._cfg.normalize_std

        def make(resize, crop=None, flip=False):
            ops = [resize]
            if crop is not None:
                ops.append(crop)
            if flip:
                ops.append(transforms.Lambda(lambda x: transforms.functional.hflip(x)))
            ops.extend([
                transforms.ToTensor(),
                transforms.Normalize(mean=mean, std=std),
            ])
            return transforms.Compose(ops)

        return [
            make(transforms.Resize((size, size))),
            make(transforms.Resize((size, size)), flip=True),
            make(transforms.Resize(size + 32), transforms.CenterCrop(size)),
        ]

    @torch.no_grad()
    def _predict_probs(self, image: Image.Image) -> np.ndarray:
        """Return the averaged softmax probabilities for an image."""
        model = self._load_model()
        temperature = self._cfg.temperature

        def _softmax(logits: torch.Tensor) -> np.ndarray:
            return torch.softmax(logits / temperature, dim=1)[0].cpu().numpy()

        if not self._cfg.tta_enabled:
            tensor = self.preprocess(image)
            outputs = model(tensor)
            return _softmax(outputs)

        tta_list = self._tta_transforms()
        tta_count = min(self._cfg.tta_transforms, len(tta_list))
        selected = tta_list[:tta_count]

        probs_sum = None
        for transform in selected:
            tensor = transform(image).unsqueeze(0).to(self._device)
            outputs = model(tensor)
            probs = _softmax(outputs)
            probs_sum = probs if probs_sum is None else probs_sum + probs

        return probs_sum / tta_count

    @staticmethod
    def _compute_entropy(probs: np.ndarray) -> float:
        """Return normalized Shannon entropy for the prediction distribution."""
        p = probs + 1e-10
        entropy = -(p * np.log(p)).sum()
        max_entropy = np.log(len(probs))
        return float(entropy / max_entropy)

    @torch.no_grad()
    def predict(
        self, image: Image.Image, top_k: int = 5
    ) -> Tuple[List[dict], str, float, bool]:
        """
        Run inference on a single image.

        Returns:
            predictions: List of top-k predictions with class name and confidence.
            top_class: The most likely class name.
            top_confidence: Confidence of the top class (percentage).
            is_reliable: Whether the prediction passes reliability heuristics.
        """
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        probs = self._predict_probs(image)
        top_indices = np.argsort(probs)[::-1][:top_k]

        predictions = [
            {
                "class_name": self._classes[idx],
                "confidence": round(float(probs[idx]) * 100, 2),
            }
            for idx in top_indices
        ]

        entropy = self._compute_entropy(probs)
        gap = predictions[0]["confidence"] - (
            predictions[1]["confidence"] if len(predictions) > 1 else 0.0
        )
        is_reliable = (
            entropy < self._cfg.entropy_threshold and gap > self._cfg.gap_threshold
        )

        return (
            predictions,
            predictions[0]["class_name"],
            predictions[0]["confidence"],
            is_reliable,
        )


# Module-level singleton for convenient imports.
_default_classifier: PlantDiseaseClassifier | None = None


def get_classifier() -> PlantDiseaseClassifier:
    """Return the default shared classifier instance."""
    global _default_classifier
    if _default_classifier is None:
        _default_classifier = PlantDiseaseClassifier()
    return _default_classifier
