from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import MessageCreate, MessageOut
from app.security.auth import get_current_admin

router = APIRouter()

@router.post("/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED, summary="Submit a contact message")
def create_contact_message(payload: MessageCreate, db: Session = Depends(get_db_dep)):
    message = models.Message(name=payload.name, email=payload.email, subject=payload.subject, message=payload.message)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.get("/admin/messages", response_model=list[MessageOut], summary="List all contact messages (admin)")
def list_contact_messages(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    offset = (page - 1) * size
    return db.query(models.Message).order_by(models.Message.created_at.desc()).offset(offset).limit(size).all()

@router.delete("/admin/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a contact message (admin)")
def delete_contact_message(message_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message)
    db.commit()
    return None
