from fastapi import APIRouter, HTTPException
from ..database.disease_database import load_diseases, get_disease
router = APIRouter(prefix="/api/diseases", tags=["diseases"])

@router.get("")
def diseases(): return load_diseases()

@router.get("/{disease_id}")
def disease(disease_id: str):
    item = get_disease(disease_id)
    if not item: raise HTTPException(404, "Disease not found")
    return item
