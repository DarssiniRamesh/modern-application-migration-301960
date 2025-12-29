# Module-wise LLD: FastAPI Backend (SQLite)

## Common Architecture
- App: FastAPI with CORS.
- Persistence: SQLite via SQLAlchemy or SQLModel. Single DB file stored in backend container volume.
- Structure:
  - api/routers/*.py: Route definitions.
  - domain/models.py: SQLAlchemy models.
  - schemas/*.py: Pydantic models for requests/responses.
  - services/*.py: Business logic.
  - repositories/*.py: DB CRUD operations.
  - security/*.py: JWT, password hashing (bcrypt/passlib).
  - storage/: media upload handling.

## Auth Module
- Responsibilities: Register/login/logout, identity endpoints, admin role management.
- Endpoints:
  - POST /auth/register {name, email, password}
  - POST /auth/login {email, password} -> {access_token, token_type}
  - POST /auth/logout (invalidate cookie or client-side clear)
  - GET /auth/me -> {id, name, email, roles}
- Models:
  - User(id, name, email unique, password_hash, created_at)
  - Admin(id, name, password_hash, role)
- Security:
  - JWT access tokens, httpOnly cookie optional.
  - Hashing: bcrypt via passlib.
- Errors:
  - 400 duplicate email, 401 invalid credentials.
- Pydantic DTOs:
  - RegisterRequest, LoginRequest, UserResponse, TokenResponse.

## Products Module
- Responsibilities: List, search, retrieve, create/update/delete, image upload.
- Endpoints:
  - GET /products, GET /products/{id}, GET /products/search?q=
  - POST /products (admin), PUT /products/{id} (admin), DELETE /products/{id} (admin)
  - POST /products/{id}/images (multipart)
- Models:
  - Product(id, name, details, price, image_01, image_02, image_03)
- Validation:
  - Name unique optional; price non-negative.
- Errors:
  - 404 not found, 409 conflict on duplicate name.

## Wishlist Module
- Responsibilities: Per-user wishlist CRUD.
- Endpoints:
  - GET /wishlist
  - POST /wishlist {pid}
  - DELETE /wishlist/{id}
  - DELETE /wishlist (clear)
- Behavior: Prevent duplicates.

## Cart Module
- Responsibilities: Per-user cart CRUD; quantity updates and totals.
- Endpoints:
  - GET /cart -> items and grand_total
  - POST /cart {pid, qty}
  - PATCH /cart/{id} {qty}
  - DELETE /cart/{id}
  - DELETE /cart
- Rules:
  - Merge if same product exists; min qty 1, max 99.

## Orders Module
- Responsibilities: Checkout from cart, store order and items, list my orders.
- Endpoints:
  - POST /orders (checkout) {name, number, email, method, address}
  - GET /orders (mine)
- Models:
  - Order(id, user_id, name, number, email, method, address, total_price, placed_on, payment_status)
  - OrderItem(id, order_id, pid, name, price, quantity)
- Payment status: default 'pending'.

## Admin Module
- Responsibilities: Admin-only management functions.
- Endpoints:
  - GET /admin/orders, PATCH /admin/orders/{id}/status
  - GET /admin/users, GET/POST /admin/admins
  - GET /admin/messages, DELETE /admin/messages/{id}
  - GET /admin/metrics
- Security:
  - Role guard (admin/superadmin).

## Messages Module
- Responsibilities: Contact form intake and admin viewing/deletion.
- Endpoints:
  - POST /messages
  - GET /admin/messages, DELETE /admin/messages/{id}

## Error Handling and Conventions
- Use HTTPException with detail codes; Pydantic validation errors; consistent error shape {error: {code, message}}.

## Example Directory Layout (Proposed)
- backend_api/src/
  - api/main.py
  - api/routers/{auth,products,cart,wishlist,orders,admin,messages}.py
  - domain/models.py
  - schemas/{auth.py,product.py,cart.py,wishlist.py,order.py,message.py,user.py}
  - services/{auth_service.py,...}
  - repositories/{user_repo.py,product_repo.py,...}
  - security/{jwt.py,hashing.py}
  - storage/{files.py}
  - db.py

Sources:
- E-commerce-PHP-Application-301945 flows and data model
- modern-application-migration-301960/backend_api/src/api/main.py
