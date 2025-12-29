"""
MySQL → SQLite migration script.

This script migrates data from the legacy PHP MySQL schema into the new SQLite database
using the SQLAlchemy models. It handles:
- Password hashing migration (SHA-1→PBKDF2, marks users for password reset)
- Cart/Wishlist normalization to new schema
- Order addresses parsing into Address entity
- Product images conversion (image_01/02/03 → ProductImage rows)
- Order items parsing (total_products string → OrderItem rows)
- Pricing conversion (int cents → Decimal)
- Field renames (name→title, pid→product_id, method→payment_method, etc.)
- Messages table import
- All target models: User, AdminUser, Category, Product, ProductImage, Address, Order, OrderItem, Message, Cart, Wishlist

Usage:
    python -m app.tools.mysql_to_sqlite --mode=dry-run
    python -m app.tools.mysql_to_sqlite --mode=execute --mysql-host=localhost --mysql-user=root --mysql-password=secret --mysql-db=ecom_db
    
    # CSV/JSON output available in migration_report.json and password_resets.csv
"""

import argparse
import csv
import json
import secrets
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.database import engine as sqlite_engine, SessionLocal as SQLiteSession
from app.db import models
from app.security.auth import get_password_hash


class MigrationReport:
    """Track migration actions and failures."""
    
    def __init__(self):
        self.actions: List[Dict[str, Any]] = []
        self.failures: List[Dict[str, Any]] = []
        self.users_requiring_reset: List[Dict[str, str]] = []
    
    def log_action(self, table: str, action: str, count: int, details: str = ""):
        self.actions.append({
            "table": table,
            "action": action,
            "count": count,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_failure(self, table: str, action: str, error: str, details: str = ""):
        self.failures.append({
            "table": table,
            "action": action,
            "error": error,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def log_password_reset(self, email: str, temp_password: str):
        self.users_requiring_reset.append({
            "email": email,
            "temp_password": temp_password
        })
    
    def save(self, output_path: str = "migration_report.json"):
        """Save report to JSON file."""
        report = {
            "summary": {
                "total_actions": len(self.actions),
                "total_failures": len(self.failures),
                "users_requiring_reset": len(self.users_requiring_reset)
            },
            "actions": self.actions,
            "failures": self.failures,
            "users_requiring_reset": self.users_requiring_reset,
            "generated_at": datetime.utcnow().isoformat()
        }
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {output_path}")
        
        # Also save password resets to CSV for easy distribution
        if self.users_requiring_reset:
            csv_path = "password_resets.csv"
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["email", "temp_password"])
                writer.writeheader()
                writer.writerows(self.users_requiring_reset)
            print(f"Password reset list saved to {csv_path}")


def parse_order_address(address_str: str) -> Dict[str, str]:
    """
    Parse concatenated address string from legacy orders table.
    
    Example format: "123 Main St, Apt 4, New York, NY, 10001, USA, +1234567890"
    """
    if not address_str:
        return {
            "line1": "Unknown",
            "city": "Unknown",
            "state": "Unknown",
            "postal_code": "00000",
            "country": "USA",
            "phone": None,
            "line2": None
        }
    
    parts = [p.strip() for p in address_str.split(',')]
    return {
        "line1": parts[0] if len(parts) > 0 and parts[0] else "Unknown",
        "line2": parts[1] if len(parts) > 1 and parts[1] else None,
        "city": parts[2] if len(parts) > 2 and parts[2] else "Unknown",
        "state": parts[3] if len(parts) > 3 and parts[3] else "Unknown",
        "postal_code": parts[4] if len(parts) > 4 and parts[4] else "00000",
        "country": parts[5] if len(parts) > 5 and parts[5] else "USA",
        "phone": parts[6] if len(parts) > 6 and parts[6] else None,
    }


def parse_order_products(products_str: str) -> List[Dict[str, Any]]:
    """
    Parse total_products string into OrderItem list.
    
    Example format: "Product A (2 x $19.99), Product B (1 x $29.99)"
    """
    items = []
    if not products_str:
        return items
    
    for item_str in products_str.split('),'):
        item_str = item_str.strip().rstrip(')')
        # Simple parsing: extract quantity and price
        # Format: "Product Name (qty x $price"
        try:
            if '(' in item_str and 'x' in item_str:
                name_part, rest = item_str.rsplit('(', 1)
                qty_str, price_str = rest.split('x')
                qty = int(qty_str.strip())
                price = Decimal(price_str.strip().replace('$', '').replace(',', ''))
                items.append({
                    "name": name_part.strip(),
                    "quantity": qty,
                    "unit_price": price
                })
        except Exception:
            # Skip malformed items
            continue
    
    return items


def cents_to_decimal(cents: int) -> Decimal:
    """Convert integer cents to Decimal dollars."""
    return Decimal(cents) / Decimal(100)


# PUBLIC_INTERFACE
def run_migration(
    mysql_host: str,
    mysql_port: int,
    mysql_user: str,
    mysql_password: str,
    mysql_db: str,
    dry_run: bool = True
) -> MigrationReport:
    """
    Run the complete migration from MySQL to SQLite.
    
    Migrates all tables including:
    - Categories
    - Products & ProductImage
    - Users (with Cart, Wishlist initialization)
    - AdminUser
    - Address (parsed from orders)
    - Orders & OrderItem
    - Message
    
    Password Migration Strategy:
    - SHA-1 hashes from MySQL are NOT portable to PBKDF2-SHA256
    - Generate temporary passwords for all users/admins
    - Mark all accounts for password reset (requires_reset=True for users)
    - Output CSV with temp passwords for user communication
    
    Args:
        mysql_host: MySQL server host
        mysql_port: MySQL server port
        mysql_user: MySQL username
        mysql_password: MySQL password
        mysql_db: MySQL database name
        dry_run: If True, only log actions without persisting to SQLite
    
    Returns:
        MigrationReport with actions, failures, and password resets
    """
    report = MigrationReport()
    
    try:
        # Import MySQL connector
        try:
            import pymysql  # noqa: F401
            mysql_available = True
        except ImportError:
            report.log_failure("system", "import", "pymysql not installed", "Install with: pip install pymysql")
            mysql_available = False
    
        if not mysql_available:
            print("ERROR: pymysql is required for MySQL migration. Install with: pip install pymysql")
            return report
        
        # Connect to MySQL
        mysql_conn_str = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
        mysql_engine = create_engine(mysql_conn_str)
        MySQLSession = sessionmaker(bind=mysql_engine)
        mysql_session = MySQLSession()
        
        sqlite_session = SQLiteSession()
        
        print(f"{'DRY RUN' if dry_run else 'EXECUTE'} MODE: Migrating from MySQL to SQLite")
        print(f"MySQL: {mysql_host}:{mysql_port}/{mysql_db}")
        print(f"SQLite: {sqlite_engine.url}")
        print("-" * 60)
        
        # Migrate Categories
        print("Migrating categories...")
        categories_map = {}
        try:
            result = mysql_session.execute(text("SELECT id, name FROM categories"))
            for row in result:
                cat_id, cat_name = row
                slug = cat_name.lower().replace(' ', '-').replace('&', 'and')[:160]
                if not dry_run:
                    category = models.Category(id=cat_id, name=cat_name, slug=slug)
                    sqlite_session.merge(category)
                categories_map[cat_id] = cat_name
            if not dry_run:
                sqlite_session.commit()
            report.log_action("categories", "migrated", len(categories_map))
            print(f"  ✓ Migrated {len(categories_map)} categories")
        except Exception as e:
            report.log_failure("categories", "migrate", str(e))
            print(f"  ✗ Failed: {e}")
            if not dry_run:
                sqlite_session.rollback()
        
        # Migrate Products
        print("Migrating products...")
        products_map = {}
        image_count = 0
        try:
            result = mysql_session.execute(text(
                "SELECT id, name, price, details, category_id, image_01, image_02, image_03 FROM products"
            ))
            for row in result:
                prod_id, name, price_cents, details, cat_id, img1, img2, img3 = row
                slug = name.lower().replace(' ', '-').replace('&', 'and')[:200]
                price_decimal = cents_to_decimal(price_cents) if isinstance(price_cents, int) else Decimal(str(price_cents or 0))
                
                if not dry_run:
                    product = models.Product(
                        id=prod_id,
                        title=name,
                        slug=slug,
                        description=details,
                        price=price_decimal,
                        stock=0,  # Will update based on inventory if available
                        category_id=cat_id,
                        image_url=img1 if img1 else None,
                        is_active=True
                    )
                    sqlite_session.merge(product)
                    
                    # Add additional images as ProductImage rows
                    for img_url in [img2, img3]:
                        if img_url:
                            img = models.ProductImage(product_id=prod_id, url=img_url)
                            sqlite_session.add(img)
                            image_count += 1
                
                products_map[prod_id] = name
            
            if not dry_run:
                sqlite_session.commit()
            report.log_action("products", "migrated", len(products_map))
            report.log_action("product_images", "migrated", image_count)
            print(f"  ✓ Migrated {len(products_map)} products with {image_count} additional images")
        except Exception as e:
            report.log_failure("products", "migrate", str(e))
            print(f"  ✗ Failed: {e}")
            if not dry_run:
                sqlite_session.rollback()
        
        # Migrate Users (with password reset strategy)
        print("Migrating users...")
        users_map = {}
        try:
            result = mysql_session.execute(text("SELECT id, name, email, password FROM users"))
            for row in result:
                user_id, name, email, old_password_hash = row
                
                # Generate temporary password and mark for reset
                # SHA-1 hashes cannot be converted to PBKDF2-SHA256
                temp_password = secrets.token_urlsafe(16)
                new_password_hash = get_password_hash(temp_password)
                
                if not dry_run:
                    user = models.User(
                        id=user_id,
                        name=name,
                        email=email,
                        password_hash=new_password_hash,
                        is_active=True,
                        requires_reset=True
                    )
                    sqlite_session.merge(user)
                    
                    # Create wishlist and cart
                    wishlist = models.Wishlist(user_id=user_id)
                    cart = models.Cart(user_id=user_id)
                    sqlite_session.merge(wishlist)
                    sqlite_session.merge(cart)
                
                users_map[user_id] = email
                report.log_password_reset(email, temp_password)
            
            if not dry_run:
                sqlite_session.commit()
            report.log_action("users", "migrated", len(users_map), "All users marked for password reset")
            report.log_action("carts", "initialized", len(users_map))
            report.log_action("wishlists", "initialized", len(users_map))
            print(f"  ✓ Migrated {len(users_map)} users (all require password reset)")
        except Exception as e:
            report.log_failure("users", "migrate", str(e))
            print(f"  ✗ Failed: {e}")
            if not dry_run:
                sqlite_session.rollback()
        
        # Migrate Admin Users
        print("Migrating admin users...")
        try:
            result = mysql_session.execute(text("SELECT id, name, password FROM admins"))
            admin_count = 0
            for row in result:
                admin_id, username, old_password_hash = row
                temp_password = secrets.token_urlsafe(16)
                new_password_hash = get_password_hash(temp_password)
                
                if not dry_run:
                    admin = models.AdminUser(
                        id=admin_id,
                        username=username,
                        password_hash=new_password_hash,
                        is_active=True
                    )
                    sqlite_session.merge(admin)
                
                report.log_password_reset(f"admin:{username}", temp_password)
                admin_count += 1
            
            if not dry_run:
                sqlite_session.commit()
            report.log_action("admin_users", "migrated", admin_count, "All admins require password reset")
            print(f"  ✓ Migrated {admin_count} admin users")
        except Exception as e:
            report.log_failure("admin_users", "migrate", str(e))
            print(f"  ✗ Failed: {e}")
            if not dry_run:
                sqlite_session.rollback()
        
        # Migrate Orders and OrderItems
        print("Migrating orders...")
        try:
            result = mysql_session.execute(text(
                "SELECT id, user_id, total_products, total_price, placed_on, payment_status, method, address FROM orders"
            ))
            order_count = 0
            order_item_count = 0
            address_count = 0
            
            for row in result:
                order_id, user_id, total_products, total_price, placed_on, payment_status, method, address = row
                
                # Parse address
                addr_data = parse_order_address(address) if address else parse_order_address("")
                
                # Create address record
                address_id = None
                if not dry_run and addr_data.get("line1"):
                    addr = models.Address(user_id=user_id, **addr_data)
                    sqlite_session.add(addr)
                    sqlite_session.flush()
                    address_id = addr.id
                    address_count += 1
                
                # Convert price (handle both cents int and decimal)
                total_decimal = cents_to_decimal(total_price) if isinstance(total_price, int) else Decimal(str(total_price or 0))
                
                # Create order
                if not dry_run:
                    order = models.Order(
                        id=order_id,
                        user_id=user_id,
                        status=payment_status or "pending",
                        total_amount=total_decimal,
                        payment_method=method or "cod",
                        shipping_address_id=address_id,
                        created_at=placed_on
                    )
                    sqlite_session.merge(order)
                    
                    # Parse and create order items
                    items = parse_order_products(total_products)
                    for item in items:
                        order_item = models.OrderItem(
                            order_id=order_id,
                            product_id=None,  # Can't map by name easily
                            quantity=item["quantity"],
                            unit_price=item["unit_price"]
                        )
                        sqlite_session.add(order_item)
                        order_item_count += 1
                
                order_count += 1
            
            if not dry_run:
                sqlite_session.commit()
            report.log_action("orders", "migrated", order_count)
            report.log_action("order_items", "migrated", order_item_count)
            report.log_action("addresses", "created", address_count)
            print(f"  ✓ Migrated {order_count} orders with {order_item_count} items and {address_count} addresses")
        except Exception as e:
            report.log_failure("orders", "migrate", str(e))
            print(f"  ✗ Failed: {e}")
            if not dry_run:
                sqlite_session.rollback()
        
        # Migrate Messages (if table exists)
        print("Migrating messages...")
        try:
            result = mysql_session.execute(text("SELECT id, name, email, subject, message FROM messages"))
            msg_count = 0
            for row in result:
                msg_id, name, email, subject, message = row
                if not dry_run:
                    msg = models.Message(
                        id=msg_id,
                        name=name,
                        email=email,
                        subject=subject,
                        message=message
                    )
                    sqlite_session.merge(msg)
                msg_count += 1
            
            if not dry_run:
                sqlite_session.commit()
            report.log_action("messages", "migrated", msg_count)
            print(f"  ✓ Migrated {msg_count} messages")
        except Exception as e:
            # Table might not exist
            report.log_action("messages", "skipped", 0, "Table not found or error: " + str(e))
            print(f"  ⚠ Messages table skipped: {e}")
        
        mysql_session.close()
        sqlite_session.close()
        
        print("-" * 60)
        print(f"Migration {'simulation' if dry_run else 'execution'} complete!")
        print(f"Total actions: {len(report.actions)}")
        print(f"Total failures: {len(report.failures)}")
        print(f"Users requiring password reset: {len(report.users_requiring_reset)}")
        
    except Exception as e:
        report.log_failure("system", "migration", str(e))
        print(f"CRITICAL ERROR: {e}")
    
    return report


# PUBLIC_INTERFACE
def main():
    """CLI entry point for migration script."""
    parser = argparse.ArgumentParser(description="Migrate MySQL e-commerce data to SQLite")
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run",
                        help="Dry-run mode (no writes) or execute mode")
    parser.add_argument("--mysql-host", default="localhost", help="MySQL host")
    parser.add_argument("--mysql-port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--mysql-user", required=True, help="MySQL username")
    parser.add_argument("--mysql-password", required=True, help="MySQL password")
    parser.add_argument("--mysql-db", required=True, help="MySQL database name")
    parser.add_argument("--output", default="migration_report.json", help="Output report file")
    
    args = parser.parse_args()
    
    dry_run = (args.mode == "dry-run")
    
    report = run_migration(
        mysql_host=args.mysql_host,
        mysql_port=args.mysql_port,
        mysql_user=args.mysql_user,
        mysql_password=args.mysql_password,
        mysql_db=args.mysql_db,
        dry_run=dry_run
    )
    
    report.save(args.output)
    
    if report.failures:
        print("\n⚠ Migration completed with failures. Review the report for details.")
        sys.exit(1)
    else:
        print("\n✓ Migration completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
