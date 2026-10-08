from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..config import settings
from ..services.image_processing import validate_and_open
from ..services.inference import predict
from ..services.translation import translate_result

router = APIRouter(prefix="/api", tags=["prediction"])

@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        image = validate_and_open(contents, file.content_type, settings.max_upload_mb)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    result = predict(image)
    result["date"] = datetime.now(timezone.utc).date().isoformat()
    result["translation"] = translate_result(result)
    return result
