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
