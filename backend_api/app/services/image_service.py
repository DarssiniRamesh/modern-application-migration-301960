from pathlib import Path
from app.core.config import settings


class ImageService:
    """Utility for deriving image storage paths."""

    @staticmethod
    def uploads_dir() -> Path:
        return settings.UPLOADS_DIR
