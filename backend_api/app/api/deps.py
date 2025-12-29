from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.security.auth import get_current_user as _get_current_user, get_current_admin as _get_current_admin


# PUBLIC_INTERFACE
def get_db_dep() -> Session:
    """DI wrapper to provide a SQLAlchemy session."""
    yield from get_db()


# PUBLIC_INTERFACE
def pagination_params(
    page: int = Query(1, ge=1, description="Page number (starting at 1)"),
    size: int = Query(12, ge=1, le=100, description="Page size"),
):
    """Common pagination params dependency."""
    return page, size


# PUBLIC_INTERFACE
def current_user(db: Session = Depends(get_db_dep)):
    """Return the authenticated user."""
    return _get_current_user(db=db)


# PUBLIC_INTERFACE
def current_admin(db: Session = Depends(get_db_dep)):
    """Return the authenticated admin user."""
    return _get_current_admin(db=db)
