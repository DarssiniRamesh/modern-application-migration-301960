# Migration Plan and Next Steps

## Phase 1: Foundations
1. Define backend project structure (routers, schemas, services, repositories, security).
2. Initialize SQLite via SQLAlchemy; create models and alembic (if used) or simple create_all migration script.
3. Implement Auth with JWT and bcrypt hashing; seed an admin user.
4. Implement Products read endpoints; static file serving for images.

Risks/Mitigations:
- Password migration from SHA1: require users to reset password or implement on-login rehash to bcrypt.
- File storage paths: lock down upload directories and validate MIME/size.

Acceptance:
- Health check returns OK; can register/login; can list products.

## Phase 2: Core Commerce
1. Wishlist and Cart endpoints with per-user data.
2. Checkout: Orders with normalized order_items; ensure totals correctness; clear cart.
3. Orders listing for user; admin endpoints for order listing and payment status update.

Acceptance:
- End-to-end add to cart → checkout → order visible; admin can mark completed.

## Phase 3: Admin and Media
1. Product create/update/delete with image upload; ensure image limits (<= 2MB each).
2. Admin metrics endpoint to populate dashboard.
3. Users/admins/messages endpoints.

Acceptance:
- Admin UI can manage products and update orders; images upload/display correctly.

## Phase 4: React SPA
1. Scaffold routes and pages; implement layout and header/footer mirroring PHP.
2. Integrate Auth flows; protected routes.
3. Implement Catalog pages (home/latest, shop, search, quick view).
4. Implement Wishlist/Cart/Checkout/Orders flows.
5. Implement Admin pages incrementally.

Acceptance:
- UX parity with PHP site; flows and constraints match (quantities, totals, form validations).

## Phase 5: Testing and Parity Verification
- Unit tests for services/repositories.
- API contract tests.
- UI e2e smoke tests across critical paths.
- Parity checklist covering:
  - Feature availability
  - Navigation and routes
  - Edge cases (empty cart, duplicate wishlist)
  - Admin CRUD and status updates

## Data Migration Approach
- Option A: Cold start with empty SQLite and manual content entry via admin.
- Option B: One-time ETL from MySQL to SQLite:
  - Export products, users (excluding passwords or mapping via temporary password reset), orders (denormalize to normalized order_items).
- Validate referential integrity and image file mapping.

## Cutover Strategy
- Run in parallel environments; test React+FastAPI fully.
- Freeze writes on PHP, perform final ETL if Option B.
- DNS/app switch to SPA + API endpoints.
- Monitor errors and performance.

## Performance Considerations
- Use proper indexes in SQLite on foreign keys and frequently filtered columns.
- Paginate product listings and searches.
- Cache read-mostly endpoints at client or via HTTP caching headers.

Next Steps:
- Approve data model and API outline.
- Implement backend Phase 1 and 2.
- Begin frontend scaffolding.

Sources:
- E-commerce-PHP-Application-301945 code
- modern-application-migration-301960 backend skeleton
- modern-application-migration-301961 frontend template
