import logging
from io import BytesIO

from fastapi import APIRouter, HTTPException, UploadFile, File
from PIL import Image

from src.api.schemas import DetectResponse, PredictionItem
from src.cv import predict as run_prediction

logger = logging.getLogger(__name__)
router = APIRouter(tags=["detect"])


@router.post("/detect", response_model=DetectResponse)
async def detect(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        result = run_prediction(image, top_k=5)
        return DetectResponse(
            predictions=[PredictionItem(**p) for p in result["predictions"]],
            top_class=result["top_class"],
            top_confidence=result["top_confidence"],
        )
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}")
