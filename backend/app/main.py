from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import prediction, diseases, translation, camera

app = FastAPI(
    title="Ginger Leaf Disease Detection AI",
    version="1.0.0",
)

# CORS configuration for the frontend and backend connection
configured_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

frontend_origin = "https://ginger-leaf-ai-frontend.onrender.com"

if frontend_origin not in configured_origins:
    configured_origins.append(frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(prediction.router)
app.include_router(diseases.router)
app.include_router(translation.router)
app.include_router(camera.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_note": (
            "Predictions are disabled until a trained model "
            "and class_names.json are installed."
        ),
    }
