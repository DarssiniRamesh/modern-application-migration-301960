from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.api.deps import get_db_dep
from app.db import models
from app.db.schemas import DashboardKPIs, OrderOut
from app.security.auth import get_current_admin

router = APIRouter()

# PUBLIC_INTERFACE
@router.get(
    "/dashboard",
    response_model=DashboardKPIs,
    summary="Get admin dashboard KPIs",
    description=(
        "Retrieve comprehensive dashboard KPIs for admin overview.\n\n"
        "Returns aggregated metrics including:\n"
        "- Total registered users count\n"
        "- Total orders count across all time\n"
        "- Total revenue sum from all orders\n"
        "- Today's orders count (UTC timezone)\n"
        "- Top 5 products by quantity sold\n"
        "- Top 5 products by revenue generated\n"
        "- Low stock products (stock <= 10 units)\n"
        "- 10 most recent orders with full details\n\n"
        "Requires admin authentication via Bearer token."
    )
)
def get_admin_dashboard(
    db: Session = Depends(get_db_dep),
    admin=Depends(get_current_admin)
):
    """
    Get admin dashboard KPIs and aggregations.
    
    This endpoint computes and returns key performance indicators for the admin dashboard,
    including user counts, order statistics, revenue metrics, product performance,
    inventory alerts, and recent order history.
    
    Args:
        db: Database session dependency
        admin: Current authenticated admin user
        
    Returns:
        DashboardKPIs: Comprehensive dashboard metrics including:
            - total_users: Count of all registered users
            - total_orders: Count of all orders placed
            - total_revenue: Sum of all order amounts (Decimal)
            - today_orders: Count of orders created today (UTC)
            - top_products_by_qty: Top 5 products by quantity sold
            - top_products_by_revenue: Top 5 products by revenue
            - low_stock_products: Products with stock <= 10 units
            - recent_orders: 10 most recent orders with full details
    """
    total_users = db.query(func.count(models.User.id)).scalar() or 0
    total_orders = db.query(func.count(models.Order.id)).scalar() or 0
    total_revenue = db.query(func.sum(models.Order.total_amount)).scalar() or Decimal("0.00")
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = db.query(func.count(models.Order.id)).filter(models.Order.created_at >= today_start).scalar() or 0
    
    top_by_qty = db.query(models.Product.id, models.Product.title, func.sum(models.OrderItem.quantity).label("total_qty")).join(models.OrderItem, models.Product.id == models.OrderItem.product_id).group_by(models.Product.id).order_by(desc("total_qty")).limit(5).all()
    top_products_by_qty = [{"product_id": p.id, "product_title": p.title, "total_quantity": int(p.total_qty)} for p in top_by_qty]
    
    top_by_revenue = db.query(models.Product.id, models.Product.title, func.sum(models.OrderItem.quantity * models.OrderItem.unit_price).label("total_revenue")).join(models.OrderItem, models.Product.id == models.OrderItem.product_id).group_by(models.Product.id).order_by(desc("total_revenue")).limit(5).all()
    top_products_by_revenue = [{"product_id": p.id, "product_title": p.title, "total_revenue": str(p.total_revenue)} for p in top_by_revenue]
    
    low_stock = db.query(models.Product).filter(models.Product.stock <= 10, models.Product.is_active == True).order_by(models.Product.stock.asc()).limit(10).all()
    low_stock_products = [{"product_id": p.id, "product_title": p.title, "stock": p.stock} for p in low_stock]
    
    recent_orders = db.query(models.Order).order_by(models.Order.created_at.desc()).limit(10).all()
    
    return DashboardKPIs(
        total_users=total_users, total_orders=total_orders, total_revenue=total_revenue, today_orders=today_orders,
        top_products_by_qty=top_products_by_qty, top_products_by_revenue=top_products_by_revenue,
        low_stock_products=low_stock_products, recent_orders=[OrderOut.from_orm(o) for o in recent_orders]
    )
