from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import ProductCreate, ProductOut, ProductUpdate
from app.security.auth import get_current_admin

router = APIRouter()


@router.get("", response_model=list[ProductOut], summary="Admin list all products")
def admin_list_products(db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    return db.query(models.Product).order_by(models.Product.created_at.desc()).all()


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED, summary="Admin create product")
def admin_create_product(payload: ProductCreate, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    existing = db.query(models.Product).filter(models.Product.slug == payload.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    product = models.Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut, summary="Admin get product")
def admin_get_product(product_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product


@router.patch("/{product_id}", response_model=ProductOut, summary="Admin update product")
def admin_update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(product, k, v)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204, summary="Admin delete product")
def admin_delete_product(product_id: int, db: Session = Depends(get_db_dep), admin=Depends(get_current_admin)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return
    db.delete(product)
    db.commit()
