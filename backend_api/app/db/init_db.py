from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.db import models
from app.security.auth import get_password_hash


def seed_data(db: Session) -> None:
    # Seed Admin
    if not db.query(models.AdminUser).first():
        admin = models.AdminUser(
            username="admin",
            password_hash=get_password_hash("admin123"),
            is_active=True,
        )
        db.add(admin)
        db.commit()

    # Seed Category
    category = db.query(models.Category).filter(models.Category.slug == "games").first()
    if not category:
        category = models.Category(name="Games", slug="games")
        db.add(category)
        db.commit()
        db.refresh(category)

    # Seed Products
    if db.query(models.Product).count() == 0:
        sample_products = [
            models.Product(
                title="Space Adventure",
                slug="space-adventure",
                description="A thrilling journey through the galaxy.",
                price=Decimal("29.99"),
                stock=50,
                category_id=category.id,
                image_url="/static/uploads/space.jpg",
                is_active=True,
            ),
            models.Product(
                title="Mystic Quest",
                slug="mystic-quest",
                description="Embark on a magical quest.",
                price=Decimal("19.99"),
                stock=100,
                category_id=category.id,
                image_url="/static/uploads/mystic.jpg",
                is_active=True,
            ),
        ]
        db.add_all(sample_products)
        db.commit()


def init_db() -> None:
    """Create tables and seed initial data idempotently."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
