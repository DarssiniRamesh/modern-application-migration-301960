from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.init_db import init_db
from app.docs.openapi_overrides import openapi_tags
from app.api.routers import (
    auth as auth_router,
    users as users_router,
    products as products_router,
    cart as cart_router,
    wishlist as wishlist_router,
    orders as orders_router,
    admin_products as admin_products_router,
    admin_users as admin_users_router,
    admin_orders as admin_orders_router,
    upload as upload_router,
    health as health_router,
)

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI app with routers, CORS, static files, and OpenAPI metadata.
    """
    app = FastAPI(
        title="E-commerce API (FastAPI + SQLite)",
        description=(
            "Modernized backend for the PHP e-commerce application, implemented with FastAPI and SQLite.\n\n"
            "Use the Auth endpoints to obtain a JWT token, then explore protected endpoints in the Swagger UI.\n"
            "Uploads are served under /static/uploads."
        ),
        version="1.0.0",
        openapi_tags=openapi_tags,
        contact={"name": "Migration Team", "email": "support@example.com"},
        license_info={"name": "MIT"},
    )

    # CORS - allow React app on port 3000 (and configurable origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS or ["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files for uploads
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR, html=False), name="static")

    # Include routers with tags
    app.include_router(health_router.router, tags=["Health"])
    app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
    app.include_router(users_router.router, prefix="/users", tags=["Users"])
    app.include_router(products_router.router, prefix="/products", tags=["Products"])
    app.include_router(cart_router.router, prefix="/cart", tags=["Cart"])
    app.include_router(wishlist_router.router, prefix="/wishlist", tags=["Wishlist"])
    app.include_router(orders_router.router, prefix="/orders", tags=["Orders"])
    app.include_router(admin_products_router.router, prefix="/admin/products", tags=["Admin Products"])
    app.include_router(admin_users_router.router, prefix="/admin/users", tags=["Admin Users"])
    app.include_router(admin_orders_router.router, prefix="/admin/orders", tags=["Admin Orders"])
    app.include_router(upload_router.router, prefix="/admin/upload", tags=["Uploads"])

    @app.on_event("startup")
    async def on_startup():
        # Initialize database and seed idempotently
        init_db()

    return app


# PUBLIC_INTERFACE
app = create_app()
