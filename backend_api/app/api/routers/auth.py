"""
User authentication router.

Provides endpoints for user registration, login, and profile retrieval.
Admin authentication is handled separately in the admin_auth router.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import UserRegister, UserLogin, Token, UserOut
from app.security.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
)
from app.core.config import settings

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserOut,
    summary="Register a new user",
    description="Register a new user with a unique email.",
)
def register_user(payload: UserRegister, db: Session = Depends(get_db_dep)):
    """
    Register a new user account.
    
    Creates a new user with the provided name, email, and password.
    Email must be unique. Automatically creates associated wishlist and cart.
    """
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


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    summary="Login as user",
    description="Authenticate user and return JWT access token.",
)
def login_user(payload: UserLogin, db: Session = Depends(get_db_dep)):
    """
    Authenticate user and return JWT token.
    
    Validates email and password, then generates a JWT token with user-scoped claims.
    The token should be used in the Authorization header as "Bearer <token>".
    """
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token(
        f"user:{user.id}",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    description="Return the current authenticated user's profile.",
)
def me(user=Depends(get_current_user)):
    """
    Return the current authenticated user's profile.
    
    Requires valid user JWT token in Authorization header.
    """
    return user
