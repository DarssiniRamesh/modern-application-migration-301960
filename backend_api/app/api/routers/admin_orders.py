from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import OrderOut
from app.security.auth import get_current_admin

router = APIRouter(tags=["Admin Orders"])

# PUBLIC_INTERFACE
@router.get("", response_model=list[OrderOut], summary="Admin list orders")
def admin_list_orders(db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """List all orders for admin."""
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()

# PUBLIC_INTERFACE
@router.get("/{order_id}", response_model=OrderOut, summary="Admin get order")
def admin_get_order(order_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """Get order by id."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

# PUBLIC_INTERFACE
@router.patch("/{order_id}", response_model=OrderOut, summary="Admin update order status")
def admin_update_order(order_id: int, status_value: str = Query(..., description="New status value"), db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """Update order status."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.status = status_value
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

# PUBLIC_INTERFACE
@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Admin delete order",
    description="Delete an order by ID (admin only).\n\nOnly allowed if order status is 'pending' or 'cancelled'.\nReturns 409 Conflict if trying to delete a fulfilled/shipped order.",
)
def admin_delete_order(order_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """Delete an order only if in allowed states."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if str(order.status).lower() not in {"pending", "cancelled"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order cannot be deleted in its current state")
    db.delete(order)
    db.commit()
    return
