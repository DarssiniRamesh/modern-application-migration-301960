from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr, conint, constr

# PUBLIC_INTERFACE
class Token(BaseModel):
    """Bearer token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type, typically 'bearer'")

# PUBLIC_INTERFACE
class UserRegister(BaseModel):
    """Register a new user."""
    name: constr(min_length=1, max_length=120) = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Unique email address")
    password: constr(min_length=6, max_length=128) = Field(..., description="Password")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr = Field(..., description="Email address")
    password: constr(min_length=6, max_length=128) = Field(..., description="Password")

# PUBLIC_INTERFACE
class AdminLogin(BaseModel):
    """Admin login schema."""
    username: constr(min_length=3, max_length=120) = Field(..., description="Admin username")
    password: constr(min_length=6, max_length=128) = Field(..., description="Password")

# PUBLIC_INTERFACE
class AdminRegister(BaseModel):
    """Admin registration schema."""
    username: constr(min_length=3, max_length=120) = Field(..., description="Admin username")
    password: constr(min_length=6, max_length=128) = Field(..., description="Password")

# PUBLIC_INTERFACE
class AddressIn(BaseModel):
    """Input schema for creating/updating an Address."""
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None

# PUBLIC_INTERFACE
class AddressOut(AddressIn):
    """Output schema for Address."""
    id: int

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class UserOut(BaseModel):
    """User profile output schema."""
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    addresses: List[AddressOut] = []

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class UserUpdate(BaseModel):
    """Update current user profile."""
    name: Optional[constr(min_length=1, max_length=120)] = None
    address: Optional[AddressIn] = None

# PUBLIC_INTERFACE
class CategoryOut(BaseModel):
    """Category details."""
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class ProductImageOut(BaseModel):
    """Product image representation."""
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

# PUBLIC_INTERFACE
class ProductCreate(ProductBase):
    """Create product schema."""
    pass

# PUBLIC_INTERFACE
class ProductUpdate(BaseModel):
    """Update product schema."""
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

# PUBLIC_INTERFACE
class ProductOut(ProductBase):
    """Product output schema."""
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageOut] = []

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class PageMeta(BaseModel):
    """Pagination metadata."""
    page: int
    size: int
    total: int

# PUBLIC_INTERFACE
class PaginatedProducts(BaseModel):
    """Paginated product list."""
    items: List[ProductOut]
    meta: PageMeta

# PUBLIC_INTERFACE
class WishlistItemIn(BaseModel):
    """Add product to wishlist."""
    product_id: int

# PUBLIC_INTERFACE
class WishlistItemOut(BaseModel):
    """Wishlist item output."""
    id: int
    product: ProductOut

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class WishlistOut(BaseModel):
    """Wishlist output."""
    id: int
    items: List[WishlistItemOut]

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class CartItemIn(BaseModel):
    """Add item to cart."""
    product_id: int
    quantity: conint(ge=1, le=99) = 1

# PUBLIC_INTERFACE
class CartItemUpdate(BaseModel):
    """Update quantity of item in cart."""
    quantity: conint(ge=1, le=99)

# PUBLIC_INTERFACE
class CartItemOut(BaseModel):
    """Cart item output."""
    id: int
    product: ProductOut
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class CartOut(BaseModel):
    """Cart output."""
    id: int
    items: List[CartItemOut]
    total: Decimal

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class CheckoutAddress(BaseModel):
    """Address payload used during checkout."""
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None

# PUBLIC_INTERFACE
class CheckoutIn(BaseModel):
    """Checkout request body."""
    payment_method: str = Field(..., description="Payment method label (e.g. 'cod', 'paypal')")
    address: CheckoutAddress

# PUBLIC_INTERFACE
class OrderItemOut(BaseModel):
    """Order item output."""
    id: int
    product_id: Optional[int]
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class OrderOut(BaseModel):
    """Order output including items."""
    id: int
    status: str
    total_amount: Decimal
    payment_method: str
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class AdminUserOut(BaseModel):
    """Admin profile output."""
    id: int
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class AdminUserUpdate(BaseModel):
    """Admin self-update schema."""
    username: Optional[constr(min_length=3, max_length=120)] = None

# PUBLIC_INTERFACE
class MessageCreate(BaseModel):
    """Contact message creation schema."""
    name: constr(min_length=1, max_length=120) = Field(..., description="Name")
    email: EmailStr = Field(..., description="Email address")
    subject: Optional[constr(max_length=200)] = Field(None, description="Subject")
    message: constr(min_length=1) = Field(..., description="Message content")

# PUBLIC_INTERFACE
class MessageOut(BaseModel):
    """Contact message output schema."""
    id: int
    name: str
    email: str
    subject: Optional[str]
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


# PUBLIC_INTERFACE
class DashboardKPIs(BaseModel):
    """Admin dashboard KPIs and aggregates.

    Includes:
    - total_users: Total registered users
    - total_orders: Total orders across all time
    - total_revenue: Total revenue across all orders (Decimal compatible; serialized as string)
    - today_orders: Number of orders placed today (UTC)
    - top_products_by_qty: Top products by quantity sold (list of dicts)
    - top_products_by_revenue: Top products by revenue (list of dicts)
    - low_stock_products: Products with low stock (<=10 units) (list of dicts)
    - recent_orders: Recent orders rendered as OrderOut
    """
    total_users: int = Field(..., description="Total registered users")
    total_orders: int = Field(..., description="Total orders placed")
    total_revenue: Decimal = Field(..., description="Total revenue across all orders")
    today_orders: int = Field(..., description="Orders placed today")

    # Using plain dicts for product aggregates to keep payload flexible
    top_products_by_qty: List[dict] = Field(default_factory=list, description="Top products by quantity sold")
    top_products_by_revenue: List[dict] = Field(default_factory=list, description="Top products by revenue")
    low_stock_products: List[dict] = Field(default_factory=list, description="Products with low stock (<=10)")
    recent_orders: List["OrderOut"] = Field(default_factory=list, description="Recent orders")

    class Config:
        from_attributes = True
