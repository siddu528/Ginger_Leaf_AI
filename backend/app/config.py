from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    google_cloud_project: str = ""
    google_application_credentials: str = ""
    esp32_cam_url: str = ""

    model_path: str = str(
        ROOT / "models" / "ginger_disease_model.keras"
    )

    confidence_threshold: float = 0.70
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_upload_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        extra="ignore"
    )


settings = Settings()