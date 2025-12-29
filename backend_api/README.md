# E-commerce FastAPI Backend (SQLite)

Modernized backend for the PHP e-commerce app, implemented with FastAPI and SQLite.

## Features
- JWT Auth for users and admins
- Product catalog with search, filters, pagination
- Wishlist and Cart management
- Checkout with Orders and Order Items
- Admin APIs for products, users, and orders
- Image upload to local storage (served via /static/uploads)
- OpenAPI docs at /docs and /redoc
- SQLite database auto-initialized and seeded on startup

## Setup

Create/activate a virtual environment, then install dependencies:

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

## Run locally

From the backend_api directory:

# Option A (used by preview tooling)
uvicorn src.api.main:app --host 0.0.0.0 --port 3002

# Option B (direct)
uvicorn app.main:app --host 0.0.0.0 --port 3002

Open Swagger UI:
http://localhost:3002/docs

Health check:
http://localhost:3002/health

## Troubleshooting

If you see errors like ModuleNotFoundError: No module named 'sqlalchemy':
- Ensure your virtual environment is active
- Run: pip install -r requirements.txt
- Confirm you are in the backend_api directory when launching uvicorn
- Both entrypoints are supported:
  - uvicorn src.api.main:app
  - uvicorn app.main:app

If imports fail with path issues, ensure the working directory is backend_api. The src/api/main.py adds backend_api to sys.path to assist preview environments.

## Environment variables
Provide these via a .env file (example):

- JWT_SECRET_KEY (required for production; default is insecure)
- ACCESS_TOKEN_EXPIRE_MINUTES (default 60)
- CORS_ALLOW_ORIGINS (comma-separated origins)
- SITE_URL (for redirects if needed)
- SQLITE_DB_FILE (path to SQLite db file; default data/app.db)
- DATABASE_URL (override full SQLAlchemy URL)

## Data and Uploads

- SQLite DB: data/app.db (auto-created)
- Uploads: static/uploads (URLs start with /static/uploads)

## Migration from MySQL

See app/tools/mysql_to_sqlite.py for the migration outline and TODOs to import legacy PHP data.

## Testing notes

- Health: GET /health
- Products: GET /products?page=1&size=12&sort=latest
- Use examples in app/docs/examples.http
