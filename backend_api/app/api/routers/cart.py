from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db.schemas import CartOut, CartItemIn, CartItemUpdate
from app.security.auth import get_current_user
from app.services.cart_service import CartService

router = APIRouter()


@router.get("", response_model=CartOut, summary="Get my cart")
def get_cart(db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Get the authenticated user's cart and total."""
    svc = CartService(db)
    cart, total = svc.get_or_create_cart_with_total(user.id)
    return {"id": cart.id, "items": cart.items, "total": total}


@router.post("", response_model=CartOut, summary="Add or update product in cart")
def add_or_update_cart(payload: CartItemIn, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """
    Add a product to the cart or update its quantity if already present.
    Quantity must be within 1..99.
    """
    svc = CartService(db)
    cart, _ = svc.add_or_update_item(user.id, payload.product_id, payload.quantity)
    total = svc.compute_total(cart)
    return {"id": cart.id, "items": cart.items, "total": total}


@router.patch("/{product_id}", response_model=CartOut, summary="Update quantity of product")
def update_quantity(product_id: int, payload: CartItemUpdate, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Update the quantity of a product in the cart."""
    svc = CartService(db)
    cart, _ = svc.add_or_update_item(user.id, product_id, payload.quantity, replace=True)
    total = svc.compute_total(cart)
    return {"id": cart.id, "items": cart.items, "total": total}


@router.delete("/{product_id}", response_model=CartOut, summary="Remove product from cart")
def remove_item(product_id: int, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Remove a product from the cart."""
    svc = CartService(db)
    cart = svc.remove_item(user.id, product_id)
    total = svc.compute_total(cart)
    return {"id": cart.id, "items": cart.items, "total": total}


@router.delete("", response_model=CartOut, summary="Clear cart")
def clear_cart(db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Clear all items from the cart."""
    svc = CartService(db)
    cart = svc.clear_cart(user.id)
    total = svc.compute_total(cart)
    return {"id": cart.id, "items": cart.items, "total": total}
