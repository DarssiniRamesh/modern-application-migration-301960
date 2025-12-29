from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db.schemas import CheckoutIn, OrderOut
from app.security.auth import get_current_user
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/checkout", response_model=OrderOut, summary="Checkout and create order")
def checkout(payload: CheckoutIn, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """
    Create an order from the current user's cart.
    Validates stock, decrements inventory, and clears cart.
    """
    svc = OrderService(db)
    order = svc.checkout(user_id=user.id, method=payload.payment_method, address=payload.address)
    return order


@router.get("", response_model=list[OrderOut], summary="List my orders")
def list_my_orders(db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """List orders belonging to the current user."""
    svc = OrderService(db)
    return svc.list_user_orders(user.id)


@router.get("/{order_id}", response_model=OrderOut, summary="Get my order details")
def get_my_order(order_id: int, db: Session = Depends(get_db_dep), user=Depends(get_current_user)):
    """Get a specific order by ID for the current user."""
    svc = OrderService(db)
    order = svc.get_user_order(user.id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
