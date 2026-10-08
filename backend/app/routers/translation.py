from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..services.translation import translate_to_kannada
router = APIRouter(prefix="/api", tags=["translation"])
class TranslationRequest(BaseModel): text: str = Field(min_length=1, max_length=10000)
@router.post("/translate")
def translate(body: TranslationRequest): return {"language":"kn", "translation":translate_to_kannada(body.text)}
