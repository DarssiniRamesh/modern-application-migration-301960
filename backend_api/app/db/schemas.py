from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr, conint, constr


# Common
class Message(BaseModel):
    detail: str = Field(..., description="Human-readable message")


# Auth
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type, typically 'bearer'")

class UserRegister(BaseModel):
    name: constr(min_length=1, max_length=120) = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Unique email address")
    password: constr(min_length=6, max_length=128) = Field(..., description="Password")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    password: constr(min_length=6, max_length=128) = Field(..., description="Password")

class AdminLogin(BaseModel):
    username: constr(min_length=3, max_length=120) = Field(..., description="Admin username")
    password: constr(min_length=6, max_length=128) = Field(..., description="Password")


# Users
class AddressIn(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None

class AddressOut(AddressIn):
    id: int

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    addresses: List[AddressOut] = []

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=120)] = None
    # For simplicity, only allow name updates and address updates
    address: Optional[AddressIn] = None


# Categories and Products
class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

class ProductImageOut(BaseModel):
    id: int
    url: str
    alt_text: Optional[str] = None

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageOut] = []

    class Config:
        from_attributes = True


# Pagination
class PageMeta(BaseModel):
    page: int
    size: int
    total: int

class PaginatedProducts(BaseModel):
    items: List[ProductOut]
    meta: PageMeta


# Wishlist
class WishlistItemIn(BaseModel):
    product_id: int

class WishlistItemOut(BaseModel):
    id: int
    product: ProductOut

    class Config:
        from_attributes = True

class WishlistOut(BaseModel):
    id: int
    items: List[WishlistItemOut]

    class Config:
        from_attributes = True


# Cart
class CartItemIn(BaseModel):
    product_id: int
    quantity: conint(ge=1, le=99) = 1

class CartItemUpdate(BaseModel):
    quantity: conint(ge=1, le=99)

class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True

class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    total: Decimal

    class Config:
        from_attributes = True


# Orders
class CheckoutAddress(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None

class CheckoutIn(BaseModel):
    payment_method: str = Field(..., description="Payment method label (e.g. 'cod', 'paypal')")
    address: CheckoutAddress

class OrderItemOut(BaseModel):
    id: int
    product_id: Optional[int]
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    payment_method: str
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True


# Admin Users
class AdminUserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
