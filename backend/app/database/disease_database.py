import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_FILE = ROOT / "config" / "diseases.json"

def load_diseases():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def get_disease(disease_id: str):
    return next((d for d in load_diseases() if d["id"].lower() == disease_id.lower()), None)
