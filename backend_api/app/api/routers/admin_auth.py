from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import AdminRegister, AdminLogin, AdminUserOut, AdminUserUpdate, Token
from app.security.auth import create_access_token, get_password_hash, verify_password, get_current_admin
from app.core.config import settings

router = APIRouter()

@router.post("/auth/register", response_model=AdminUserOut, summary="Register a new admin")
def register_admin(payload: AdminRegister, db: Session = Depends(get_db_dep)):
    existing = db.query(models.AdminUser).filter(models.AdminUser.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    admin = models.AdminUser(username=payload.username, password_hash=get_password_hash(payload.password), is_active=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@router.post("/auth/login", response_model=Token, summary="Login as admin")
def login_admin(payload: AdminLogin, db: Session = Depends(get_db_dep)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(f"admin:{admin.id}", expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=token, token_type="bearer")

@router.get("/me", response_model=AdminUserOut, summary="Get current admin profile")
def get_admin_me(admin=Depends(get_current_admin)):
    return admin

@router.put("/me", response_model=AdminUserOut, summary="Update current admin profile")
def update_admin_me(payload: AdminUserUpdate, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    if payload.username:
        existing = db.query(models.AdminUser).filter(models.AdminUser.username == payload.username, models.AdminUser.id != admin.id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Username already taken")
        admin.username = payload.username
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@router.get("/admins", response_model=list[AdminUserOut], summary="List all admins")
def list_admins(db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    return db.query(models.AdminUser).order_by(models.AdminUser.created_at.desc()).all()
