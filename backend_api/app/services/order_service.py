from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.db import models
from app.services.cart_service import CartService


class OrderService:
    """Service handling checkout and order management."""

    def __init__(self, db: Session):
        self.db = db
        self.cart_svc = CartService(db)

    def checkout(self, user_id: int, method: str, address) -> models.Order:
        cart = self.cart_svc.get_or_create_cart(user_id)
        if not cart.items:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Validate stock
        for item in cart.items:
            if item.product is None or item.product.stock < item.quantity:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product id {item.product_id}")

        # Create or get address record
        addr = models.Address(
            user_id=user_id,
            line1=address.line1,
            line2=address.line2,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,
            phone=address.phone,
        )
        self.db.add(addr)
        self.db.commit()
        self.db.refresh(addr)

        order = models.Order(
            user_id=user_id,
            status="pending",
            total_amount=Decimal("0.00"),
            payment_method=method,
            shipping_address_id=addr.id,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        total = Decimal("0.00")
        for item in list(cart.items):
            # Decrement stock
            item.product.stock -= item.quantity
            self.db.add(item.product)

            oi = models.OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            self.db.add(oi)
            total += Decimal(item.unit_price) * item.quantity

        order.total_amount = total
        self.db.add(order)

        # Clear cart
        for item in list(cart.items):
            self.db.delete(item)

        self.db.commit()
        self.db.refresh(order)
        return order

    def list_user_orders(self, user_id: int):
        return self.db.query(models.Order).filter(models.Order.user_id == user_id).order_by(models.Order.created_at.desc()).all()

    def get_user_order(self, user_id: int, order_id: int) -> Optional[models.Order]:
        return self.db.query(models.Order).filter(models.Order.user_id == user_id, models.Order.id == order_id).first()
