# Current Architecture: HLD and LLD (PHP Monolith)

## High-Level Design (HLD)
- System Context: A single monolithic PHP web application serves both storefront and admin back office. All pages are rendered server-side with embedded PHP. Users interact over HTTP; state is maintained with PHP sessions.
- Containers:
  - Web/App: Apache + PHP interpreter.
  - Database: MySQL (shop_db).
  - Static Assets: Served by Apache (css, js, images).
- Modules and Interactions:
  - Auth: Session-based login/logout; user and admin areas separated by session keys (user_id vs admin_id).
  - Catalog: Product listing, search, quick view; reads products table.
  - Cart/Wishlist: Table-backed per-user lists with form posts.
  - Checkout/Orders: Writes orders and clears cart; read-only order history.
  - Admin: CRUD on products, orders status updates, users, admins, messages handling.
- Request Flows:
  - Typical request includes: include connect.php, start session, determine user_id/admin_id, optionally include wishlist_cart.php for side-effect form handling, execute DB operations via PDO, render HTML with values.

## Low-Level Design (LLD)
- PHP File Structure:
  - Root pages: home.php, shop.php, search_page.php, quick_view.php, cart.php, checkout.php, orders.php, about.php, contact.php, user_login.php, user_register.php, update_user.php, wishlist.php.
  - Components: components/connect.php, user_header.php, footer.php, wishlist_cart.php, admin_header.php, user_logout.php, admin_logout.php.
  - Admin: admin/index.php (login), dashboard.php, products.php, update_product.php, placed_orders.php, messages.php, users_accounts.php, admin_accounts.php, register_admin.php, update_profile.php.
  - Assets: css/, js/, images/, uploaded_img/.
- Session Handling:
  - session_start() on most pages.
  - $_SESSION['user_id'] and $_SESSION['admin_id'] used to gate actions and content.
- DB Access Patterns:
  - PDO with prepared statements (INSERT/UPDATE/DELETE/SELECT).
  - Connect via components/connect.php with hard-coded DSN and credentials.
- Includes and Shared UI:
  - user_header.php prints notices based on $message[] and renders counts for wishlist/cart via DB queries per request.
  - footer.php common footer.
  - wishlist_cart.php contains side-effect handlers for POST add_to_cart/add_to_wishlist.
- Data Handling:
  - Input sanitization with filter_var and basic length constraints in HTML.
  - Passwords hashed with SHA1 on users/admins.
  - orders.total_products is a concatenated human-readable string rather than normalized line items.
- Admin Specifics:
  - File uploads managed in products.php with size checks and move_uploaded_file.
  - Deleting a product cascades manual deletions in cart and wishlist, and unlinks files.

Sources:
- E-commerce-PHP-Application-301945/admin/*.php, components/*.php, root pages, shop_db.sql
