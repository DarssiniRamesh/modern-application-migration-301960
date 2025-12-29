"""
Contact message submission and management endpoints.

This module provides:
- Public endpoint for submitting contact messages
- Admin endpoints for listing and deleting contact messages with pagination
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import MessageCreate, MessageOut
from app.security.auth import get_current_admin

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a contact message",
    description=(
        "Submit a contact message from the public contact form.\n\n"
        "This is a public endpoint that does not require authentication. "
        "Users can submit inquiries, feedback, or support requests.\n\n"
        "**Rate Limiting:** In production, this endpoint should be rate-limited "
        "to prevent abuse (e.g., 5 requests per minute per IP).\n\n"
        "**Fields:**\n"
        "- name: Full name of the sender (required, max 120 chars)\n"
        "- email: Email address for response (required, must be valid email)\n"
        "- subject: Optional subject line (max 200 chars)\n"
        "- message: Message content (required, min 1 char)\n\n"
        "**Returns:** The created message with ID and timestamp."
    ),
    operation_id="create_contact_message",
    responses={
        201: {"description": "Message successfully created"},
        422: {"description": "Validation error (invalid email, missing required fields, etc.)"},
    },
)
def create_contact_message(
    payload: MessageCreate,
    db: Session = Depends(get_db_dep)
):
    """
    Submit a public contact message.
    
    Creates a new contact message record in the database. This endpoint is public
    and does not require authentication, allowing visitors to submit inquiries.
    
    TODO: Implement rate limiting (e.g., slowapi, Redis-based limiter) to prevent spam.
    Recommended: 5 requests per minute per IP address.
    
    Args:
        payload: Message data (name, email, subject, message)
        db: Database session dependency
        
    Returns:
        MessageOut: Created message with id, timestamps, and all submitted fields
    """
    # Create message record
    message = models.Message(
        name=payload.name,
        email=payload.email,
        subject=payload.subject,
        message=payload.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


# PUBLIC_INTERFACE
@router.get(
    "/admin/messages",
    response_model=list[MessageOut],
    summary="List all contact messages (admin)",
    description=(
        "Retrieve a paginated list of all contact messages (admin only).\n\n"
        "Returns messages in reverse chronological order (newest first). "
        "Use pagination parameters to navigate through results.\n\n"
        "**Authentication:** Requires admin Bearer token.\n\n"
        "**Pagination:**\n"
        "- page: Page number, starting at 1 (default: 1)\n"
        "- size: Items per page, 1-100 (default: 20)\n\n"
        "**Returns:** Array of message objects with full details including "
        "sender info, subject, message content, and creation timestamp."
    ),
    operation_id="list_contact_messages",
    responses={
        200: {"description": "List of contact messages"},
        401: {"description": "Not authenticated or invalid admin token"},
    },
)
def list_contact_messages(
    page: int = Query(1, ge=1, description="Page number (starting at 1)"),
    size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    db: Session = Depends(get_db_dep),
    admin=Depends(get_current_admin)
):
    """
    List all contact messages with pagination (admin only).
    
    Retrieves contact messages in reverse chronological order with pagination support.
    Admins can use this to review customer inquiries and support requests.
    
    Args:
        page: Page number (1-indexed)
        size: Number of items per page (1-100)
        db: Database session dependency
        admin: Current authenticated admin user
        
    Returns:
        list[MessageOut]: List of message objects for the requested page
    """
    offset = (page - 1) * size
    messages = (
        db.query(models.Message)
        .order_by(models.Message.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return messages


# PUBLIC_INTERFACE
@router.delete(
    "/admin/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a contact message (admin)",
    description=(
        "Delete a contact message by ID (admin only).\n\n"
        "Permanently removes a contact message from the database. "
        "This action cannot be undone.\n\n"
        "**Authentication:** Requires admin Bearer token.\n\n"
        "**Use Cases:**\n"
        "- Removing spam or irrelevant messages\n"
        "- Cleaning up resolved inquiries\n"
        "- Managing database storage\n\n"
        "**Returns:** 204 No Content on success."
    ),
    operation_id="delete_contact_message",
    responses={
        204: {"description": "Message successfully deleted"},
        401: {"description": "Not authenticated or invalid admin token"},
        404: {"description": "Message not found"},
    },
)
def delete_contact_message(
    message_id: int,
    db: Session = Depends(get_db_dep),
    admin=Depends(get_current_admin)
):
    """
    Delete a contact message (admin only).
    
    Permanently deletes a contact message by ID. Returns 404 if the message
    doesn't exist.
    
    Args:
        message_id: ID of the message to delete
        db: Database session dependency
        admin: Current authenticated admin user
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if message not found
    """
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    return None
