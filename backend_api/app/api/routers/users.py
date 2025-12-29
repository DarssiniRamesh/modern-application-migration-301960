from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import UserOut, UserUpdate, AddressIn
from app.security.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserOut, summary="Get my profile")
def get_me(user=Depends(get_current_user)):
    """Get the current user's profile and addresses."""
    return user


@router.patch("/me", response_model=UserOut, summary="Update my profile")
def update_me(payload: UserUpdate, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """
    Update the current user's profile.
    Allows updating name and optionally an address (create if not exists).
    """
    updated = False
    if payload.name:
        user.name = payload.name
        updated = True

    if payload.address:
        addr: AddressIn = payload.address
        # If user has no addresses, create one; else update the first one
        first_addr = db.query(models.Address).filter(models.Address.user_id == user.id).first()
        if not first_addr:
            new_addr = models.Address(
                user_id=user.id,
                line1=addr.line1,
                line2=addr.line2,
                city=addr.city,
                state=addr.state,
                postal_code=addr.postal_code,
                country=addr.country,
                phone=addr.phone,
            )
            db.add(new_addr)
        else:
            first_addr.line1 = addr.line1
            first_addr.line2 = addr.line2
            first_addr.city = addr.city
            first_addr.state = addr.state
            first_addr.postal_code = addr.postal_code
            first_addr.country = addr.country
            first_addr.phone = addr.phone
        updated = True

    if updated:
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
