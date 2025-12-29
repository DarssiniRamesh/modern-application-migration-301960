from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.api.deps import get_db_dep, pagination_params
from app.db import models
from app.db.schemas import CategoryOut, ProductOut, PaginatedProducts, PageMeta

router = APIRouter()


@router.get("/categories", response_model=list[CategoryOut], summary="List categories")
def list_categories(db: Session = Depends(get_db_dep)):
    """Return all product categories."""
    return db.query(models.Category).order_by(models.Category.name.asc()).all()


@router.get("", response_model=PaginatedProducts, summary="List products")
def list_products(
    db: Session = Depends(get_db_dep),
    params=Depends(pagination_params),
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[int] = Query(None, description="Category ID filter"),
    sort: Optional[str] = Query("latest", description="Sort by: latest|price_asc|price_desc"),
):
    """List products with pagination, search, and filters."""
    page, size = params
    query = db.query(models.Product).filter(models.Product.is_active == True)

    if q:
        like = f"%{q}%"
        query = query.filter(models.Product.title.ilike(like))
    if category:
        query = query.filter(models.Product.category_id == category)

    if sort == "price_asc":
        query = query.order_by(asc(models.Product.price))
    elif sort == "price_desc":
        query = query.order_by(desc(models.Product.price))
    else:
        query = query.order_by(desc(models.Product.created_at))

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return PaginatedProducts(items=items, meta=PageMeta(page=page, size=size, total=total))


@router.get("/{id_or_slug}", response_model=ProductOut, summary="Get product by ID or slug")
def get_product(id_or_slug: str, db: Session = Depends(get_db_dep)):
    """Get a single product by numeric ID or slug string."""
    product = None
    if id_or_slug.isdigit():
        product = db.query(models.Product).filter(models.Product.id == int(id_or_slug)).first()
    if not product:
        product = db.query(models.Product).filter(models.Product.slug == id_or_slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
