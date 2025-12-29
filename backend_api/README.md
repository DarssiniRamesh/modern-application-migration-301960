# E-commerce FastAPI Backend (SQLite)

Modernized backend for the PHP e-commerce app, implemented with FastAPI and SQLite.

## Features

- JWT Auth for users and admins
- Product catalog with search, filters, pagination
- Wishlist and Cart management
- Checkout with Orders and Order Items
- Admin APIs for products, users, and orders
- **Admin Dashboard** with KPIs and aggregations
- **Admin self-management** (register, profile, list admins)
- **Contact messages** (public submission, admin management)
- Image upload with **MIME type and size validation**
- **Product name uniqueness** enforcement with 409 responses
- **Wishlist clear-all** endpoint
- **Admin order deletion** with status validation
- OpenAPI docs at /docs and /redoc (with Bearer token auth)
- SQLite database auto-initialized and seeded on startup
- **Comprehensive MySQL→SQLite migration script**

## Setup

Create/activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run Locally

From the backend_api directory:

```bash
# Option A (used by preview tooling)
uvicorn src.api.main:app --host 0.0.0.0 --port 3002

# Option B (direct)
uvicorn app.main:app --host 0.0.0.0 --port 3002
```

Open Swagger UI:
http://localhost:3002/docs

**Authorize in Swagger UI:**
1. Call POST /auth/login (for users) or POST /auth/admin/login (for admins)
2. Copy access_token from the response
3. Click the "Authorize" button in Swagger UI
4. In the BearerAuth dialog, paste the access_token (no need to prefix with "Bearer ")
5. Try protected endpoints (they show a lock icon); public endpoints work without auth

Health check:
http://localhost:3002/health

## Data Migration

### MySQL to SQLite Migration

The project includes a comprehensive migration script to migrate data from the legacy PHP MySQL database to SQLite.

#### Prerequisites

Install pymysql for MySQL connectivity:
```bash
pip install pymysql
```

#### Usage

**Dry-run mode** (no data written, generates report only):
```bash
python -m app.tools.mysql_to_sqlite \
  --mode=dry-run \
  --mysql-host=localhost \
  --mysql-user=root \
  --mysql-password=your_password \
  --mysql-db=ecom_db
```

**Execute mode** (performs actual migration):
```bash
python -m app.tools.mysql_to_sqlite \
  --mode=execute \
  --mysql-host=localhost \
  --mysql-user=root \
  --mysql-password=your_password \
  --mysql-db=ecom_db \
  --output=migration_report.json
```

#### Migration Features

The migration script handles:
- **Password hashing migration**: All users/admins are marked for password reset and assigned temporary passwords (saved to `password_resets.csv`)
- **Cart/Wishlist normalization**: Legacy cart/wishlist data normalized to new schema
- **Order addresses**: Concatenated address strings parsed into Address entities
- **Product images**: `image_01`, `image_02`, `image_03` fields converted to ProductImage rows
- **Order items**: `total_products` string parsed into individual OrderItem rows
- **Pricing conversion**: Integer cents converted to Decimal(12,2)
- **Field mapping**: Legacy field names mapped to new schema (name→title, pid→product_id, method→payment_method, etc.)
- **Messages**: Contact messages imported if table exists

#### Migration Output

- `migration_report.json`: Detailed JSON report of all actions, failures, and statistics
- `password_resets.csv`: List of users/admins with temporary passwords for distribution

## New Features

### Admin Dashboard (`GET /admin/dashboard`)

Returns comprehensive KPIs including:
- Total users, orders, and revenue
- Today's orders count
- Top products by quantity and revenue (top 5 each)
- Low stock products (stock ≤ 10)
- Recent orders (last 10)

Uses efficient SQLAlchemy queries with aggregates and joins.

### Admin Self-Management

- `POST /admin/auth/register`: Register new admin
- `POST /admin/auth/login`: Admin login (returns JWT)
- `GET /admin/me`: Get current admin profile
- `PUT /admin/me`: Update admin profile (username)
- `GET /admin/admins`: List all admins

### Contact Messages

- `POST /contact/messages`: Public endpoint to submit contact messages (no auth required)
- `GET /contact/admin/messages`: Admin endpoint to list messages with pagination
- `DELETE /contact/admin/messages/{id}`: Admin endpoint to delete messages

### Enhanced Features

- **Product name uniqueness**: Enforced at database level with unique constraint; returns 409 Conflict on duplicates during create/update
- **Upload validations**: 
  - MIME type validation (only image/jpeg, image/png, image/webp allowed)
  - Size limit (max 5MB)
  - Returns 413 Payload Too Large for oversized files
  - Returns 415 Unsupported Media Type for invalid MIME types
  - Sanitized filename generation with UUID
- **Wishlist clear-all**: `DELETE /wishlist` removes all items (idempotent, returns 204)
- **Admin order deletion**: `DELETE /admin/orders/{id}` only allows deletion of pending/cancelled orders; returns 409 Conflict for fulfilled/shipped orders

## API Examples

See `app/docs/examples.http` for comprehensive HTTP request examples for all endpoints, including:
- User registration and authentication
- Product browsing and search
- Cart and wishlist operations
- Checkout and orders
- Admin dashboard and KPIs
- Admin product/user/order management
- Contact message submission and admin management
- File uploads with validation

## Environment Variables

Provide these via a .env file:

- `JWT_SECRET_KEY` (required for production; default is insecure)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60)
- `CORS_ALLOW_ORIGINS` (comma-separated origins)
- `SITE_URL` (for redirects if needed)
- `SQLITE_DB_FILE` (path to SQLite db file; default data/app.db)
- `DATABASE_URL` (override full SQLAlchemy URL)

## Data and Uploads

- SQLite DB: `data/app.db` (auto-created on first run)
- Uploads: `static/uploads/` (served at `/static/uploads/`)

## Troubleshooting

If you see errors like `ModuleNotFoundError: No module named 'sqlalchemy'`:
- Ensure your virtual environment is active
- Run: `pip install -r requirements.txt`
- Confirm you are in the backend_api directory when launching uvicorn
- Both entrypoints are supported:
  - `uvicorn src.api.main:app`
  - `uvicorn app.main:app`

If imports fail with path issues, ensure the working directory is `backend_api`. The `src/api/main.py` adds `backend_api` to `sys.path` to assist preview environments.

## Architecture

- **Models**: SQLAlchemy ORM models in `app/db/models.py`
- **Schemas**: Pydantic request/response models in `app/db/schemas.py`
- **Routers**: FastAPI route handlers in `app/api/routers/`
- **Services**: Business logic in `app/services/`
- **Security**: JWT auth and password hashing in `app/security/auth.py`
- **Migration**: MySQL→SQLite migration script in `app/tools/mysql_to_sqlite.py`

## Testing

Use the examples in `app/docs/examples.http` with REST Client extensions (VS Code, IntelliJ) or tools like curl/httpie/Postman.

Key test flows:
1. Register user → Login → Add to cart → Checkout
2. Admin login → Create product → Update stock → View dashboard
3. Submit contact message → Admin view messages → Delete message
4. Upload product image with various MIME types and sizes

## Deployment

For production:
1. Set strong `JWT_SECRET_KEY` in environment
2. Configure CORS origins appropriately
3. Use a production ASGI server (uvicorn with gunicorn, hypercorn, etc.)
4. Consider migrating to PostgreSQL for better concurrency (SQLite is great for dev/demo)
5. Set up proper file storage (S3, CDN) for uploads in production environments

## License

MIT
