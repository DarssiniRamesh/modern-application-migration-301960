# Current Implementation Detailing (PHP E-commerce App)

## Functional Overview
The PHP application is a monolithic e-commerce site (GameZone branding) built on a LAMP stack with a MySQL database. It provides:
- Authentication: User registration, login, logout, and profile update (user_register.php, user_login.php, update_user.php). Sessions are used to track logged-in users via $_SESSION['user_id'].
- Catalog: Latest products carousel on home.php; product grids on shop.php and search_page.php; per-product quick view via quick_view.php.
- Cart and Wishlist: Add to wishlist/cart from listings and quick view using components/wishlist_cart.php; manage cart (quantity update, delete item, clear all) in cart.php; wishlist management in wishlist.php.
- Checkout and Orders: Checkout flow in checkout.php with address capture and payment method selection (no actual gateway); order creation persists to orders table and clears the cart; orders.php lists user orders.
- Admin: Admin login (admin/index.php), dashboard (admin/dashboard.php), product management with image upload (admin/products.php, admin/update_product.php), order management (admin/placed_orders.php), user and admin account management (admin/users_accounts.php, admin/admin_accounts.php), messages (admin/messages.php).

## Key Pages, Templates, Includes, and Navigation
- Includes:
  - components/connect.php: Creates a PDO connection to MySQL.
  - components/user_header.php: Renders the main header with logo, navigation, icons for search, wishlist count, cart count, and user profile menu incorporating session state.
  - components/footer.php: Footer with quick links and contact info.
  - components/wishlist_cart.php: Processes POST forms for add_to_wishlist and add_to_cart actions. Redirects to login when user is anonymous.
  - components/admin_header.php: Admin navigation and alerts.
- Pages:
  - home.php: Hero sliders (Swiper.js) with GameZone assets; latest products slider querying products LIMIT 6.
  - shop.php: Full product list with add-to-cart and wishlist controls.
  - search_page.php: Search box and results filtered by name LIKE query.
  - quick_view.php: Detailed view with additional images and details field.
  - cart.php: Lists user’s cart items, quantity editing, per-item delete, delete all, grand total; proceed to checkout if total > 0.
  - checkout.php: Lists current order items and grand total; collects name, number, email, address lines, city/state/country, pin code; supports method values: cash on delivery, credit card, paytm, paypal.
  - orders.php: Shows user’s prior orders with payment status coloring.
  - about.php, contact.php: Static and form page respectively; contact form writes into messages.
- Navigation: user_header.php links to home, about, orders, shop, contact, with search, wishlist, and cart icons. Footer repeats key navigation.
- Assets: css/style.css; js/script.js for user UI; Swiper.js via CDN; Font Awesome via CDN; images in images/ and uploaded_img/ for product images.

## Data Model and Entities
The shop_db.sql defines MySQL tables (types simplified):
- users: id (PK), name, email, password (SHA1 hashed).
- admins: id (PK), name, password (SHA1 hashed).
- products: id (PK), name, details, price, image_01, image_02, image_03.
- cart: id (PK), user_id (FK), pid (FK products.id), name, price, quantity, image.
- wishlist: id (PK), user_id (FK), pid (FK products.id), name, price, image.
- orders: id (PK), user_id (FK), name, number, email, method, address, total_products (concatenated string), total_price, placed_on (timestamp default CURRENT_TIMESTAMP), payment_status (pending|completed).
- messages: id (PK), user_id (FK), name, email, number, message.

## Integrations and 3rd-Party Libraries
- Database: MySQL accessed through PDO (components/connect.php).
- HTTP server: Apache (assumed by LAMP; README mentions typical deployment).
- Front-end libraries: Swiper.js carousel via CDN, Font Awesome icon fonts via CDN.

## Deployment and Runtime Context
- Classic LAMP: Apache serves PHP; MySQL hosts shop_db; phpMyAdmin dump provided.
- Environment: Database connection hard-coded in connect.php:
  - host: vincedarshini.webhop.me
  - dbname: shop_db
  - user: root
  - password: password
- Session handling via PHP session_start() and $_SESSION for user/admin IDs.

## Request Flows (Examples)
- Add to cart: User submits POST form with pid, name, price, image, qty; components/wishlist_cart.php validates session and inserts into cart; if item in wishlist, it is removed.
- Checkout: checkout.php aggregates cart items and total, collects address and method, inserts into orders, then deletes cart rows for user.
- Admin product CRUD: admin/products.php handles add with image upload and server-side size checks; delete path also purges related cart/wishlist entries and unlinks uploaded images.

Sources: 
- E-commerce-PHP-Application-301945/home.php, shop.php, search_page.php, quick_view.php, cart.php, checkout.php, orders.php, user_login.php, user_register.php
- E-commerce-PHP-Application-301945/admin/*.php, components/*.php
- E-commerce-PHP-Application-301945/shop_db.sql
- E-commerce-PHP-Application-301945/js/script.js, css/style.css
