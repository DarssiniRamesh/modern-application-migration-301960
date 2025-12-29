from decimal import Decimal
from sqlalchemy.orm import Session

from app.db import models


class CartService:
    """Service for managing cart content and totals."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_cart(self, user_id: int) -> models.Cart:
        cart = self.db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
        if not cart:
            cart = models.Cart(user_id=user_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        return cart

    def compute_total(self, cart: models.Cart) -> Decimal:
        total = Decimal("0.00")
        for item in cart.items:
            total += Decimal(item.unit_price) * item.quantity
        return total

    def get_or_create_cart_with_total(self, user_id: int):
        cart = self.get_or_create_cart(user_id)
        total = self.compute_total(cart)
        return cart, total

    def add_or_update_item(self, user_id: int, product_id: int, quantity: int, replace: bool = False):
        cart = self.get_or_create_cart(user_id)
        product = self.db.query(models.Product).filter(models.Product.id == product_id, models.Product.is_active == True).first()
        if not product:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Product not found")
        item = self.db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id, models.CartItem.product_id == product_id).first()
        if not item:
            item = models.CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity, unit_price=product.price)
            self.db.add(item)
        else:
            item.quantity = quantity if replace else max(1, min(99, item.quantity + quantity))
        self.db.commit()
        self.db.refresh(cart)
        return cart, item

    def remove_item(self, user_id: int, product_id: int):
        cart = self.get_or_create_cart(user_id)
        item = self.db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id, models.CartItem.product_id == product_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()
        self.db.refresh(cart)
        return cart

    def clear_cart(self, user_id: int):
        cart = self.get_or_create_cart(user_id)
        for item in list(cart.items):
            self.db.delete(item)
        self.db.commit()
        self.db.refresh(cart)
        return cart
