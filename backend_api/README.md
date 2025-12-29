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

## Run locally

1. Create a virtualenv and install deps:

   pip install -r requirements.txt

2. Start the server (port 3002 typical in this environment):

   uvicorn app.main:app --host 0.0.0.0 --port 3002 --reload

3. Open Swagger UI:

   http://localhost:3002/docs

## API Quickstart

- Register a user: POST /auth/register
- Login: POST /auth/login -> copy access_token from response
- Authorize: click "Authorize" in Swagger and paste: `Bearer <access_token>`
- Explore protected endpoints (Cart, Wishlist, Orders, Users)
- Admin login: POST /auth/admin/login (default seed: username=admin password=admin123)

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
