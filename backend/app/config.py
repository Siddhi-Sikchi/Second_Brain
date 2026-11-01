import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load .env file
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Second Brain AI")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./second_brain.db")

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "second-brain-super-secret-key-change-in-production-random-hash-token"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25"))

    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # CORS
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def upload_path(self) -> Path:
        base = Path(__file__).resolve().parent.parent
        upload_folder = base / self.UPLOAD_DIR.lstrip("./")
        upload_folder.mkdir(parents=True, exist_ok=True)
        return upload_folder


settings = Settings()
