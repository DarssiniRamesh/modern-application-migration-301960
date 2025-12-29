import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from starlette import status

from app.core.config import settings
from app.security.auth import get_current_admin

router = APIRouter()


@router.post("", summary="Upload image", status_code=status.HTTP_201_CREATED)
def upload_image(file: UploadFile = File(...), admin=Depends(get_current_admin)):
    """
    Upload an image file to the local uploads directory.
    Returns the public URL for the uploaded file.
    """
    filename = file.filename or "upload.bin"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    content = file.file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")
    new_name = f"{uuid4().hex}{ext}"
    dest_path = settings.UPLOADS_DIR / new_name
    with open(dest_path, "wb") as f:
        f.write(content)
    return {"url": f"/static/uploads/{new_name}"}
