from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import prediction, diseases, translation, camera

app = FastAPI(title="Ginger Leaf Disease Detection AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(prediction.router)
app.include_router(diseases.router)
app.include_router(translation.router)
app.include_router(camera.router)

@app.get("/api/health")
def health(): return {"status":"ok", "model_note":"Predictions are disabled until a trained model and class_names.json are installed."}
