from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import WishlistOut, WishlistItemIn
from app.security.auth import get_current_user

router = APIRouter()


@router.get("", response_model=WishlistOut, summary="Get my wishlist")
def get_wishlist(db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Return the user's wishlist."""
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).first()
    if not wishlist:
        wishlist = models.Wishlist(user_id=user.id)
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)
    return wishlist


@router.post("", response_model=WishlistOut, summary="Add product to wishlist")
def add_to_wishlist(payload: WishlistItemIn, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Add a product to the wishlist, ignoring duplicates."""
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).first()
    if not wishlist:
        wishlist = models.Wishlist(user_id=user.id)
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)

    product = db.query(models.Product).filter(models.Product.id == payload.product_id, models.Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    exists = db.query(models.WishlistItem).filter(
        models.WishlistItem.wishlist_id == wishlist.id,
        models.WishlistItem.product_id == product.id
    ).first()
    if not exists:
        db.add(models.WishlistItem(wishlist_id=wishlist.id, product_id=product.id))
        db.commit()

    db.refresh(wishlist)
    return wishlist


@router.delete("/{product_id}", response_model=WishlistOut, summary="Remove product from wishlist")
def remove_from_wishlist(product_id: int, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Remove a product from the wishlist."""
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    item = db.query(models.WishlistItem).filter(
        models.WishlistItem.wishlist_id == wishlist.id,
        models.WishlistItem.product_id == product_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
    db.refresh(wishlist)
    return wishlist
