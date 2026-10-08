from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl
from ..config import settings
router = APIRouter(prefix="/api/camera", tags=["camera"])
class ESP32Config(BaseModel): url: HttpUrl

@router.get("/status")
def status(): return {"esp32_url": settings.esp32_cam_url, "configured": bool(settings.esp32_cam_url)}

@router.post("/esp32")
def configure(body: ESP32Config):
    settings.esp32_cam_url = str(body.url)
    return {"configured": True, "url": settings.esp32_cam_url}
