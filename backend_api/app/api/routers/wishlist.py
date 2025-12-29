from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import WishlistOut, WishlistItemIn
from app.security.auth import get_current_user

router = APIRouter(tags=["Wishlist"])

# PUBLIC_INTERFACE
@router.get("", response_model=WishlistOut, summary="Get my wishlist", description="Return the user's wishlist.")
def get_wishlist(db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Return or create the current user's wishlist with items."""
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).first()
    if not wishlist:
        wishlist = models.Wishlist(user_id=user.id)
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)
    return wishlist

# PUBLIC_INTERFACE
@router.post("", response_model=WishlistOut, summary="Add product to wishlist", description="Add a product to the wishlist, ignoring duplicates.")
def add_to_wishlist(payload: WishlistItemIn, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Add product to wishlist if not present (idempotent)."""
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).first()
    if not wishlist:
        wishlist = models.Wishlist(user_id=user.id)
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)

    product = db.query(models.Product).filter(models.Product.id == payload.product_id, models.Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing = db.query(models.WishlistItem).filter(
        models.WishlistItem.wishlist_id == wishlist.id,
        models.WishlistItem.product_id == payload.product_id
    ).first()
    if not existing:
        db.add(models.WishlistItem(wishlist_id=wishlist.id, product_id=payload.product_id))
        db.commit()

    db.refresh(wishlist)
    return wishlist

# PUBLIC_INTERFACE
@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="Clear entire wishlist", description="Remove all items from the current user's wishlist.\n\nIdempotent operation - returns 204 No Content whether wishlist was empty or not.")
def clear_wishlist(db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Clear all wishlist items for current user, return 204."""
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).first()
    if wishlist:
        db.query(models.WishlistItem).filter(models.WishlistItem.wishlist_id == wishlist.id).delete()
        db.commit()
    return

# PUBLIC_INTERFACE
@router.delete("/{product_id}", response_model=WishlistOut, summary="Remove product from wishlist", description="Remove a product from the wishlist.")
def remove_from_wishlist(
    product_id: int = Path(..., ge=1),
    db: Session = Depends(get_db_dep),
    user=Depends(get_current_user),
):
    """Remove a single product from wishlist and return updated wishlist."""
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).first()
    if not wishlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist not found")
    db.query(models.WishlistItem).filter(
        models.WishlistItem.wishlist_id == wishlist.id,
        models.WishlistItem.product_id == product_id
    ).delete()
    db.commit()
    db.refresh(wishlist)
    return wishlist
