# Migration Goals and Modules

## Goal
Migrate the PHP monolithic e-commerce application to a modern architecture with:
- FastAPI backend persisting to SQLite (constraint: must use SQLite, not MySQL).
- React SPA frontend delivering equivalent UX and feature parity with existing flows (auth, catalog, cart/wishlist, checkout, orders, admin).

## Scope and Parity
- Maintain existing features, page flows, and GameZone branding elements where appropriate.
- Preserve behaviors: latest products, quick view, search/shop, cart quantity update and totals, checkout address and method, admin CRUD (products with image upload), users, orders, admin accounts, and messages.

## Target Modules
- Backend (FastAPI + SQLite):
  - Auth: User and admin authentication; token-based (proposed JWT) with refresh optional; password hashing upgrade from SHA1.
  - Catalog: Products read endpoints; search; quick view; image management.
  - Cart/Wishlist: Per-user collections; merging logic; quantity updates; grand total computation.
  - Checkout/Orders: Order creation; payment status updates (admin); order listing by user; admin management.
  - Admin Management: Products CRUD with image upload endpoints; users/admins management; messages; dashboards/metrics endpoints.
  - Shared: Domain models (Pydantic), repositories, services, error handling, pagination/sorting, CORS.
- Frontend (React SPA):
  - Auth: Login/register forms, protected routes, session/JWT handling.
  - Catalog: Home (latest), Shop, Search, Quick View detail.
  - Cart/Wishlist: Add/remove, quantity updates, totals, clear all.
  - Checkout/Orders: Checkout form; order confirmation; order history.
  - Admin: Products CRUD, users, orders, admins, messages dashboards and forms.
  - Shared: Routing, global state (e.g., React Query or Context/Reducer), components for headers/footers, sliders, icons.

## Session/Auth Strategy
- Replace PHP sessions with stateless JWT access tokens (and optional refresh) stored in httpOnly cookies or memory + CSRF protections.
- Password hashing: migrate to modern hashing (e.g., passlib/bcrypt) and enforce migration path for existing users.

Sources:
- E-commerce-PHP-Application-301945 code review and shop_db.sql
- modern-application-migration-301960/backend_api/src/api/main.py and interfaces/openapi.json
- modern-application-migration-301961/frontend_app/src/App.js
