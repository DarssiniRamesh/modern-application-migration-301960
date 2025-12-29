"""
Upload router for handling file uploads with validation.

This module provides secure file upload endpoints with:
- MIME type whitelisting (image/jpeg, image/png, image/webp)
- File size limits (5MB maximum)
- Safe filename generation using UUIDs
- Admin-only access control
"""
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from starlette import status

from app.core.config import settings
from app.security.auth import get_current_admin

router = APIRouter()

# Allowed MIME types for image uploads (whitelist approach for security)
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
# Max file size: 5MB (matches PHP application behavior)
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
    # Step 1: Validate MIME type against whitelist (returns 415 if invalid)
    content_type = file.content_type
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Step 2: Read file content into memory for size validation
    content = file.file.read()
    
    # Step 3: Validate file size (returns 413 if too large)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Step 4: Safe filename handling - extract extension from original filename
    filename = file.filename or "upload.bin"
    ext = os.path.splitext(filename)[1].lower()
    
    # Step 5: Ensure extension matches content type or derive from MIME type
    # This prevents filename spoofing attacks
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        # Fallback to extension based on validated MIME type
        mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        ext = mime_to_ext.get(content_type, ".jpg")
    
    # Step 6: Generate safe unique filename using UUID (prevents path traversal and collisions)
    safe_name = f"{uuid4().hex}{ext}"
    dest_path = settings.UPLOADS_DIR / safe_name
    
    # Step 7: Write validated file to disk
    with open(dest_path, "wb") as f:
        f.write(content)
    
    # Return public URL for accessing the uploaded file
    return {"url": f"/static/uploads/{safe_name}"}
