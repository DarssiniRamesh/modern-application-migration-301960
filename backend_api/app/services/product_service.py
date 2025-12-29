from sqlalchemy.orm import Session


class ProductService:
    """Product-related business logic (search/filter helpers)."""

    def __init__(self, db: Session):
        self.db = db
