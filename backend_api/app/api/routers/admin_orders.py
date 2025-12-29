from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import OrderOut
from app.security.auth import get_current_admin

router = APIRouter()


@router.get("", response_model=list[OrderOut], summary="Admin list orders")
def admin_list_orders(db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderOut, summary="Admin get order")
def admin_get_order(order_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    return order


@router.patch("/{order_id}", response_model=OrderOut, summary="Admin update order status")
def admin_update_order(order_id: int, status_value: str, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    order.status = status_value
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=204, summary="Admin delete order")
def admin_delete_order(order_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """
    Delete an order by ID (admin only).
    
    Only allowed if order status is 'pending' or 'cancelled'.
    Returns 409 Conflict if trying to delete a fulfilled/shipped order.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only allow deletion of pending or cancelled orders
    if order.status not in ["pending", "cancelled"]:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete order with status '{order.status}'. Only 'pending' or 'cancelled' orders can be deleted."
        )
    
    db.delete(order)
    db.commit()
    return None
