"""
MySQL → SQLite migration outline.

This script documents the steps to migrate data from the legacy PHP MySQL schema
into the new SQLite database using the SQLAlchemy models in this project.

TODOs:
- Provide MySQL connection details via environment variables or a config file
- Map legacy table fields to the new normalized schema (notably orders/order_items)
- Handle password hashing migration (Users/Admins): consider resetting to bcrypt

This script does not run automatically and is safe to keep in the repo as guidance.
"""

from typing import Any

# Pseudocode outline:
# 1) Connect to MySQL (e.g., using mysqlclient or pymysql) - NOT included as dependency yet.
# 2) Connect to SQLite using app.db.database.engine and SessionLocal.
# 3) For each table (users, admins, categories, products, wishlist, cart, orders...), read rows,
#    transform to match models, and insert using the ORM.
# 4) For orders: denormalize legacy orders.total_products string into individual OrderItem rows.
# 5) For images: copy files from legacy upload directory into app/static/uploads and update URLs.

# Example skeleton structure:
def run_migration(mysql_conn_params: dict[str, Any]) -> None:
    """
    Run the migration from MySQL to SQLite.

    Args:
        mysql_conn_params: Dictionary containing host, port, user, password, database, etc.

    Steps:
    - Establish MySQL connection (TODO)
    - Read batches per table
    - Insert into SQLite via SQLAlchemy session
    - Commit in chunks and handle FKs order (categories -> products -> carts/wishlists -> orders)
    """
    # TODO: Implement connection to MySQL using a chosen client (e.g., pymysql)
    # TODO: Implement data mapping functions per table
    # TODO: Insert rows into SQLite session
    raise NotImplementedError("Implement actual ETL when MySQL source is available.")
