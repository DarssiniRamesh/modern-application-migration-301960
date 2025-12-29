"""
Upload router for handling file uploads with validation.

- MIME type: image/jpeg, image/png, image/webp
- File size: <= 5MB
- Safe filename generation
- Admin-only access
"""
import os
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status

from app.core.config import settings
from app.security.auth import get_current_admin

router = APIRouter(tags=["Uploads"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def _derive_ext_from_mime(mime: str) -> str:
    return { "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp" }.get(mime, ".jpg")

# PUBLIC_INTERFACE
@router.post("/admin/upload", summary="Upload image", status_code=status.HTTP_201_CREATED, description="Upload an image file to the local uploads directory.\n\nValidates:\n- MIME type (must be image/jpeg, image/png, or image/webp)\n- File size (must be <= 5MB)\n\nReturns the public URL for the uploaded file.\n\nHTTP Status Codes:\n- 201: Successfully uploaded\n- 413: File too large (>5MB)\n- 415: Unsupported media type (invalid MIME type)")
def upload_image(file: UploadFile = File(...), admin=Depends(get_current_admin)):
    """Validate, store and return public URL for uploaded image."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Allowed: image/jpeg, image/png, image/webp",
        )

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 5MB",
        )

    original_ext = os.path.splitext(file.filename or "upload")[1].lower()
    ext = original_ext if original_ext in (".jpg", ".jpeg", ".png", ".webp") else _derive_ext_from_mime(file.content_type)
    if ext == ".jpeg":
        ext = ".jpg"

    safe_name = f"{uuid4().hex}{ext}"
    dest_dir: Path = settings.UPLOADS_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / safe_name

    with open(dest_path, "wb") as f:
        f.write(content)

    return {"url": f"/static/uploads/{safe_name}"}
