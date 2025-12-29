from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import UserRegister, UserLogin, AdminLogin, Token, UserOut
from app.security.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
)
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserOut, summary="Register a new user")
def register_user(payload: UserRegister, db: Session = Depends(get_db_dep)):
    """Register a new user with a unique email."""
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create associated wishlist and cart records
    wishlist = models.Wishlist(user_id=user.id)
    cart = models.Cart(user_id=user.id)
    db.add_all([wishlist, cart])
    db.commit()

    return user


@router.post("/login", response_model=Token, summary="Login as user")
def login_user(payload: UserLogin, db: Session = Depends(get_db_dep)):
    """Authenticate user and return JWT access token."""
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(f"user:{user.id}", expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=token, token_type="bearer")


@router.post("/admin/login", response_model=Token, summary="Login as admin")
def login_admin(payload: AdminLogin, db: Session = Depends(get_db_dep)):
    """Authenticate admin and return JWT access token."""
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(f"admin:{admin.id}", expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserOut, summary="Get current user")
def me(user=Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return user
