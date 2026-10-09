
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import prediction, diseases, translation, camera

app = FastAPI(
    title="Ginger Leaf Disease Detection AI",
    version="1.0.0",
)

# Frontend URL
frontend_origin = "https://ginger-leaf-ai-frontend.onrender.com"

# Read configured CORS origins
configured_origins = [
    origin.strip().rstrip("/")
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

# Add the deployed frontend if it is not already present
if frontend_origin not in configured_origins:
    configured_origins.append(frontend_origin)

# Enable CORS
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
