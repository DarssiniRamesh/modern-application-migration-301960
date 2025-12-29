from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import ProductCreate, ProductOut, ProductUpdate
from app.security.auth import get_current_admin

router = APIRouter(tags=["Admin Products"])

# PUBLIC_INTERFACE
@router.get("", response_model=list[ProductOut], summary="Admin list all products")
def admin_list_products(db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """List products for admin."""
    return db.query(models.Product).order_by(models.Product.created_at.desc()).all()

# PUBLIC_INTERFACE
@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="Admin create product", description="Create a new product (admin only).\n\nProduct title must be unique. Returns 409 Conflict if duplicate.")
def admin_create_product(payload: ProductCreate, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """Create product with unique title enforcement (409 on conflict)."""
    existing = db.query(models.Product).filter(models.Product.title == payload.title).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product title already exists")
    if db.query(models.Product).filter(models.Product.slug == payload.slug).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    product = models.Product(**payload.dict())
    try:
        db.add(product)
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product title already exists")
    return product

# PUBLIC_INTERFACE
@router.get("/{product_id}", response_model=ProductOut, summary="Admin get product")
def admin_get_product(product_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """Get product by id."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

# PUBLIC_INTERFACE
@router.patch("/{product_id}", response_model=ProductOut, summary="Admin update product", description="Update an existing product (admin only).\n\nProduct title must be unique. Returns 409 Conflict if duplicate.")
def admin_update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db_dep),
    admin=Depends(get_current_admin),
):
    """Update product with unique title check and 409 conflicts."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    data = payload.dict(exclude_unset=True)
    if "title" in data and data["title"] and data["title"] != product.title:
        dup = db.query(models.Product).filter(models.Product.title == data["title"], models.Product.id != product.id).first()
        if dup:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product title already exists")
    if "slug" in data and data["slug"] and data["slug"] != product.slug:
        if db.query(models.Product).filter(models.Product.slug == data["slug"], models.Product.id != product.id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")

    for k, v in data.items():
        setattr(product, k, v)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product title already exists")
    return product

# PUBLIC_INTERFACE
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Admin delete product")
def admin_delete_product(product_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    """Delete product by id."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return
    db.delete(product)
    db.commit()
    return
