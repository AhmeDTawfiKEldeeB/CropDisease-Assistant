"""Convenience prediction functions used by the API."""

import logging
from typing import Any, Dict

from PIL import Image

from src.cv.classifier import get_classifier

logger = logging.getLogger(__name__)


def predict(image: Image.Image, top_k: int = 5) -> Dict[str, Any]:
    """
    Predict plant disease from an image.

    Args:
        image: A PIL image.
        top_k: Number of top predictions to return.

    Returns:
        A dictionary with predictions, top_class, top_confidence and is_reliable.
    """
    classifier = get_classifier()
    predictions, top_class, top_confidence, is_reliable = classifier.predict(
        image, top_k=top_k
    )
    return {
        "predictions": predictions,
        "top_class": top_class,
        "top_confidence": top_confidence,
        "is_reliable": is_reliable,
    }
