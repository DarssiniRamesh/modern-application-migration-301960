from typing import Any, Callable, Dict, List

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


openapi_tags = [
    {"name": "Health", "description": "Health and readiness checks."},
    {"name": "Auth", "description": "User and admin authentication endpoints."},
    {"name": "Users", "description": "User profile management."},
    {"name": "Products", "description": "Product catalog browse and search."},
    {"name": "Wishlist", "description": "Wishlist operations for authenticated users."},
    {"name": "Cart", "description": "Shopping cart operations for authenticated users."},
    {"name": "Orders", "description": "Checkout and order history for authenticated users."},
    {"name": "Admin Products", "description": "Admin-only product management."},
    {"name": "Admin Users", "description": "Admin-only user management."},
    {"name": "Admin Orders", "description": "Admin-only order management."},
    {"name": "Uploads", "description": "Admin-only file uploads."},
]


def _is_public_path(path: str, method_spec: Dict[str, Any]) -> bool:
    """
    Determine if a route should remain public in docs.
    Public endpoints include:
      - GET /health
      - /auth/register
      - /auth/login
      - /auth/admin/login
      - /products (list/detail)
      - /products/categories
    All others are considered protected and will have BearerAuth added.

    Note: Some protected routes may already carry explicit security in code;
    this function preserves existing explicit security if present.
    """
    # If security is explicitly empty list ([]), keep it public
    if "security" in method_spec and method_spec["security"] == []:
        return True

    path_lower = path.lower()
    # Health
    if path_lower == "/health":
        return True

    # Auth public endpoints
    if path_lower in ("/auth/register", "/auth/login", "/auth/admin/login"):
        return True

    # Products public endpoints
    if path_lower.startswith("/products"):
        # All GETs under /products are public in this app (list, detail, categories)
        return True

    # Otherwise protected by default
    return False


# PUBLIC_INTERFACE
def build_custom_openapi(app: FastAPI) -> Callable[[], Dict[str, Any]]:
    """
    Returns an app.openapi override that:
      - Generates the base schema with FastAPI's get_openapi (avoids recursion)
      - Adds components.securitySchemes.BearerAuth (HTTP bearer, JWT format)
      - Applies security=[{"BearerAuth": []}] to protected endpoints
      - Leaves public endpoints without security
    """

    def custom_openapi() -> Dict[str, Any]:
        # Serve from cache if already computed
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema  # type: ignore[return-value]

        # Generate a base schema using FastAPI's utility to avoid recursion
        openapi_schema: Dict[str, Any] = get_openapi(
            title=app.title or "API",
            version=app.version or "0.1.0",
            description=app.description or "",
            routes=app.routes,
            tags=openapi_tags,
        )

        # Ensure components dict exists
        components: Dict[str, Any] = openapi_schema.setdefault("components", {})
        security_schemes: Dict[str, Any] = components.setdefault("securitySchemes", {})

        # Define the BearerAuth scheme
        security_schemes["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Paste the access_token returned by /auth/login or /auth/admin/login",
        }

        # Walk all paths/methods and set security for protected endpoints
        paths: Dict[str, Any] = openapi_schema.get("paths", {})
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, method_spec in list(path_item.items()):
                if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                    continue
                if not isinstance(method_spec, dict):
                    continue

                # If method already declares security and is using OAuth2PasswordBearer,
                # replace it with BearerAuth. Preserve other entries.
                if "security" in method_spec:
                    sec_list = method_spec.get("security") or []
                    new_sec_list: List[Dict[str, List[str]]] = []
                    for sec in sec_list:
                        if "OAuth2PasswordBearer" in sec:
                            new_sec_list.append({"BearerAuth": []})
                        else:
                            new_sec_list.append(sec)
                    method_spec["security"] = new_sec_list
                else:
                    # If not explicitly marked, compute based on our public/protected rules
                    if not _is_public_path(path, method_spec):
                        method_spec["security"] = [{"BearerAuth": []}]

        # Remove OAuth2PasswordBearer definition if present to avoid duplicating schemes
        if "OAuth2PasswordBearer" in security_schemes:
            security_schemes.pop("OAuth2PasswordBearer", None)

        # Cache and return
        app.openapi_schema = openapi_schema  # type: ignore[attr-defined]
        return openapi_schema

    return custom_openapi
