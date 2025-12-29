import os
from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings loaded from environment variables with sensible defaults."""
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    STATIC_DIR: Path = PROJECT_ROOT / "static"
    UPLOADS_DIR: Path = STATIC_DIR / "uploads"

    # Database
    SQLITE_DB_FILE: str = os.getenv("SQLITE_DB_FILE", str((PROJECT_ROOT / "data" / "app.db").resolve()))
    SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{SQLITE_DB_FILE}")

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_SUPER_SECRET")  # Request from user to set securely
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # CORS
    CORS_ALLOW_ORIGINS: list[str] = (
        os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        if os.getenv("CORS_ALLOW_ORIGINS")
        else ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # Site URL for email redirects if needed
    SITE_URL: str = os.getenv("SITE_URL", "http://localhost:3002")


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
