"""
Admin authentication and self-management router.

Provides endpoints for admin registration, login, profile management, and listing all admins.
All endpoints except registration and login require admin JWT authentication.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import AdminRegister, AdminLogin, AdminUserOut, AdminUserUpdate, Token
from app.security.auth import create_access_token, get_password_hash, verify_password, get_current_admin
from app.core.config import settings

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "/auth/register",
    response_model=AdminUserOut,
    summary="Register a new admin",
    description="""
Register a new admin user account.

Creates a new admin with the provided username and password. The username must be unique.
Password is hashed using PBKDF2-SHA256 before storage.

**Requirements:**
- Username: 3-120 characters
- Password: 6-128 characters

**Returns:**
- 200: Admin profile with id, username, is_active status, and created_at timestamp
- 400: Username already registered
- 422: Validation error (invalid input format)

**Note:** This endpoint may require existing admin authentication in production environments.
For initial setup, ensure at least one admin exists via database seeding.
    """,
    operation_id="register_admin_admin_auth_register_post",
)
def register_admin(payload: AdminRegister, db: Session = Depends(get_db_dep)):
    """Register a new admin user with unique username and hashed password."""
    existing = db.query(models.AdminUser).filter(models.AdminUser.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    admin = models.AdminUser(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


# PUBLIC_INTERFACE
@router.post(
    "/auth/login",
    response_model=Token,
    summary="Login as admin",
    description="""
Authenticate admin user and return JWT access token.

Validates username and password, then generates a JWT token with admin-scoped claims.
The token should be used in the Authorization header as "Bearer <token>" for subsequent requests.

**Requirements:**
- Valid admin username and password
- Admin account must be active (is_active=true)

**Returns:**
- 200: JWT access token with bearer type
- 401: Invalid credentials or inactive admin account
- 422: Validation error (invalid input format)

**Token Format:**
The token contains a subject claim in the format "admin:<id>" to distinguish admin tokens from user tokens.
Token expiration is configured via ACCESS_TOKEN_EXPIRE_MINUTES setting.
    """,
    operation_id="login_admin_admin_auth_login_post",
)
def login_admin(payload: AdminLogin, db: Session = Depends(get_db_dep)):
    """Authenticate admin and return JWT token for protected endpoints."""
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account is inactive"
        )
    token = create_access_token(
        f"admin:{admin.id}",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=AdminUserOut,
    summary="Get current admin profile",
    description="""
Retrieve the authenticated admin's profile information.

Returns the profile of the currently authenticated admin based on the JWT token.
Requires valid admin JWT token in Authorization header.

**Authentication:**
- Requires: Bearer token with admin scope (obtained from /admin/auth/login)

**Returns:**
- 200: Admin profile with id, username, is_active status, and created_at timestamp
- 401: Invalid or missing authentication token, or admin not found/inactive

**Use Case:**
Use this endpoint to verify admin authentication and retrieve the current admin's details.
    """,
    operation_id="get_admin_me_admin_me_get",
)
def get_admin_me(admin=Depends(get_current_admin)):
    """Return the current authenticated admin user profile."""
    return admin


# PUBLIC_INTERFACE
@router.put(
    "/me",
    response_model=AdminUserOut,
    summary="Update current admin profile",
    description="""
Update the authenticated admin's profile information.

Allows the current admin to update their own username. Password updates are not supported
through this endpoint for security reasons (use a dedicated password reset flow).

**Authentication:**
- Requires: Bearer token with admin scope (obtained from /admin/auth/login)

**Updatable Fields:**
- username: New username (must be unique across all admins)

**Returns:**
- 200: Updated admin profile
- 401: Invalid or missing authentication token
- 409: Username already taken by another admin
- 422: Validation error (invalid input format)

**Notes:**
- Only the authenticated admin can update their own profile
- Username uniqueness is enforced across all admin accounts
- Empty or null username in payload will not update the field
    """,
    operation_id="update_admin_me_admin_me_put",
)
def update_admin_me(
    payload: AdminUserUpdate,
    db: Session = Depends(get_db_dep),
    admin=Depends(get_current_admin)
):
    """Update the current admin's profile (currently supports username updates only)."""
    if payload.username:
        # Check for duplicate username (excluding current admin)
        existing = db.query(models.AdminUser).filter(
            models.AdminUser.username == payload.username,
            models.AdminUser.id != admin.id
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Username already taken")
        admin.username = payload.username
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


# PUBLIC_INTERFACE
@router.get(
    "/admins",
    response_model=list[AdminUserOut],
    summary="List all admins",
    description="""
Retrieve a list of all admin users in the system.

Returns all admin accounts ordered by creation date (newest first).
Includes both active and inactive admin accounts.

**Authentication:**
- Requires: Bearer token with admin scope (obtained from /admin/auth/login)

**Returns:**
- 200: List of all admin profiles with id, username, is_active status, and created_at timestamps
- 401: Invalid or missing authentication token

**Use Case:**
Use this endpoint for admin management dashboards to view all administrative accounts,
monitor admin activity, and verify admin account status.

**Response Format:**
Returns an array of admin profiles. Empty array if no admins exist (which should not
occur in practice as at least one admin is needed to access this endpoint).
    """,
    operation_id="list_admins_admin_admins_get",
)
def list_admins(db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """List all admin users ordered by creation date (newest first)."""
    return db.query(models.AdminUser).order_by(models.AdminUser.created_at.desc()).all()
