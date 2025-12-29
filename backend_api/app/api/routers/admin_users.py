from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import UserOut
from app.security.auth import get_current_admin

router = APIRouter()


@router.get("", response_model=list[UserOut], summary="Admin list users")
def admin_list_users(db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@router.get("/{user_id}", response_model=UserOut, summary="Admin get user")
def admin_get_user(user_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user


@router.patch("/{user_id}", response_model=UserOut, summary="Admin activate/deactivate user")
def admin_toggle_user(user_id: int, active: bool, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    user.is_active = active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
