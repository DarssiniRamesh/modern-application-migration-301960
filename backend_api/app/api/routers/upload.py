import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from starlette import status

from app.core.config import settings
from app.security.auth import get_current_admin

router = APIRouter()

# Allowed MIME types for image uploads
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
# Max file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


# PUBLIC_INTERFACE
@router.post("", summary="Upload image", status_code=status.HTTP_201_CREATED, tags=["Uploads"])
def upload_image(file: UploadFile = File(...), admin=Depends(get_current_admin)):
    """
    Upload an image file to the local uploads directory.
    
    Validates:
    - MIME type (must be image/jpeg, image/png, or image/webp)
    - File size (must be <= 5MB)
    
    Returns the public URL for the uploaded file.
    
    HTTP Status Codes:
    - 201: Successfully uploaded
    - 413: File too large (>5MB)
    - 415: Unsupported media type (invalid MIME type)
    """
    # Validate MIME type
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Read file content
    content = file.file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Sanitize filename and generate new name
    filename = file.filename or "upload.bin"
    ext = os.path.splitext(filename)[1].lower()
    
    # Ensure extension matches content type
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        # Fallback to extension based on MIME type
        mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        ext = mime_to_ext.get(content_type, ".jpg")
    
    # Generate safe unique filename
    safe_name = f"{uuid4().hex}{ext}"
    dest_path = settings.UPLOADS_DIR / safe_name
    
    # Write file
    with open(dest_path, "wb") as f:
        f.write(content)
    
    return {"url": f"/static/uploads/{safe_name}"}
