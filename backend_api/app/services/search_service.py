from sqlalchemy.orm import Session


class SearchService:
    """Search service placeholder; routers currently implement simple filtering."""
    def __init__(self, db: Session):
        self.db = db
