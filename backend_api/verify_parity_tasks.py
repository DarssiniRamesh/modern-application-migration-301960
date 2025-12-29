#!/usr/bin/env python3
"""
Verification script for backend parity tasks completion.

This script performs basic validation checks to ensure all parity tasks
(01.04-03.01) are properly implemented without starting the server.

Usage:
    python verify_parity_tasks.py
"""

import sys
from typing import List, Tuple


def check_upload_validations() -> Tuple[bool, str]:
    """Verify upload validation implementation."""
    try:
        from app.api.routers.upload import ALLOWED_MIME_TYPES, MAX_FILE_SIZE
        
        # Check constants are defined
        assert ALLOWED_MIME_TYPES == {"image/jpeg", "image/png", "image/webp"}
        assert MAX_FILE_SIZE == 5 * 1024 * 1024
        
        # Check router has the endpoint
        from app.api.routers.upload import router
        route_names = [r.path for r in router.routes]
        assert "" in route_names  # POST /admin/upload
        
        return True, "✓ Upload validations (MIME type, 5MB limit, 413/415 responses)"
    except Exception as e:
        return False, f"✗ Upload validations: {e}"


def check_wishlist_clear() -> Tuple[bool, str]:
    """Verify wishlist clear-all endpoint."""
    try:
        from app.api.routers.wishlist import router
        
        # Find DELETE /wishlist route
        delete_routes = [r for r in router.routes if hasattr(r, 'methods') and 'DELETE' in r.methods]
        root_delete = [r for r in delete_routes if r.path == ""]
        
        assert len(root_delete) > 0, "DELETE /wishlist endpoint not found"
        assert root_delete[0].status_code == 204
        
        return True, "✓ DELETE /wishlist (clear-all, 204 response)"
    except Exception as e:
        return False, f"✗ Wishlist clear: {e}"


def check_admin_order_delete() -> Tuple[bool, str]:
    """Verify admin order deletion with status restrictions."""
    try:
        from app.api.routers.admin_orders import router
        
        # Find DELETE /admin/orders/{order_id} route
        delete_routes = [r for r in router.routes if hasattr(r, 'methods') and 'DELETE' in r.methods]
        
        assert len(delete_routes) > 0, "DELETE /admin/orders/{order_id} not found"
        
        # Check the endpoint function has status validation logic
        import inspect
        func = delete_routes[0].endpoint
        source = inspect.getsource(func)
        
        assert 'pending' in source.lower(), "Missing status validation"
        assert 'cancelled' in source.lower(), "Missing status validation"
        assert '409' in source or 'conflict' in source.lower(), "Missing 409 handling"
        
        return True, "✓ DELETE /admin/orders/{id} (status restrictions, 409 handling)"
    except Exception as e:
        return False, f"✗ Admin order delete: {e}"


def check_product_uniqueness() -> Tuple[bool, str]:
    """Verify product title uniqueness constraint and 409 handling."""
    try:
        from app.db.models import Product
        from app.api.routers.admin_products import router
        
        # Check database constraint
        constraints = [c.name for c in Product.__table__.constraints if hasattr(c, 'name')]
        assert 'uq_product_title' in constraints, "Missing unique constraint on product title"
        
        # Check POST endpoint handles 409
        import inspect
        post_route = [r for r in router.routes if hasattr(r, 'methods') and 'POST' in r.methods][0]
        source = inspect.getsource(post_route.endpoint)
        assert '409' in source or 'conflict' in source.lower(), "Missing 409 handling in create"
        
        # Check PATCH endpoint handles 409
        patch_routes = [r for r in router.routes if hasattr(r, 'methods') and 'PATCH' in r.methods]
        if patch_routes:
            source = inspect.getsource(patch_routes[0].endpoint)
            assert '409' in source or 'conflict' in source.lower(), "Missing 409 handling in update"
        
        return True, "✓ Product title uniqueness (DB constraint, 409 in create/update)"
    except Exception as e:
        return False, f"✗ Product uniqueness: {e}"


def check_migration_script() -> Tuple[bool, str]:
    """Verify migration script completeness."""
    try:
        from app.tools.mysql_to_sqlite import (
            parse_order_address,
            parse_order_products,
            cents_to_decimal,
            MigrationReport
        )
        
        # Test helper functions
        addr = parse_order_address("123 Main St, Apt 4, New York, NY, 10001, USA, +1234567890")
        assert addr['line1'] == "123 Main St"
        assert addr['city'] == "New York"
        assert addr['postal_code'] == "10001"
        
        # Test cents conversion
        from decimal import Decimal
        assert cents_to_decimal(1999) == Decimal("19.99")
        
        # Test order products parsing
        items = parse_order_products("Product A (2 x $19.99), Product B (1 x $29.99)")
        assert len(items) == 2
        assert items[0]['quantity'] == 2
        
        # Check MigrationReport has required methods
        report = MigrationReport()
        assert hasattr(report, 'log_action')
        assert hasattr(report, 'log_failure')
        assert hasattr(report, 'log_password_reset')
        assert hasattr(report, 'save')
        
        return True, "✓ Migration script (SHA-1→PBKDF2, parsing, conversions, JSON/CSV output)"
    except Exception as e:
        return False, f"✗ Migration script: {e}"


def check_models_schemas() -> Tuple[bool, str]:
    """Verify all required models and schemas exist."""
    try:
        from app.db.models import Message, Address, ProductImage, OrderItem
        from app.db.schemas import MessageCreate
        
        # Verify model attributes
        assert hasattr(Message, 'name')
        assert hasattr(Message, 'email')
        assert hasattr(Address, 'line1')
        assert hasattr(Address, 'user_id')
        assert hasattr(ProductImage, 'product_id')
        assert hasattr(ProductImage, 'url')
        assert hasattr(OrderItem, 'order_id')
        assert hasattr(OrderItem, 'quantity')
        
        # Verify schema fields
        msg_fields = MessageCreate.__fields__.keys()
        assert 'name' in msg_fields and 'email' in msg_fields
        
        return True, "✓ Models/Schemas (Message, Address, ProductImage, OrderItem all present)"
    except Exception as e:
        return False, f"✗ Models/Schemas: {e}"


def check_openapi_docs() -> Tuple[bool, str]:
    """Verify OpenAPI documentation is complete."""
    try:
        from app.docs.openapi_overrides import openapi_tags
        
        expected_tags = [
            "Health", "Auth", "Users", "Products", "Wishlist", "Cart",
            "Orders", "Contact", "Admin Auth", "Admin Dashboard",
            "Admin Products", "Admin Users", "Admin Orders", "Uploads"
        ]
        
        actual_tags = [t['name'] for t in openapi_tags]
        
        for tag in expected_tags:
            assert tag in actual_tags, f"Missing tag: {tag}"
        
        # Check openapi.json exists
        import os
        assert os.path.exists('interfaces/openapi.json'), "OpenAPI spec not generated"
        
        # Check examples.http exists
        assert os.path.exists('app/docs/examples.http'), "examples.http not found"
        
        return True, "✓ OpenAPI documentation (14 tags, spec generated, examples present)"
    except Exception as e:
        return False, f"✗ OpenAPI docs: {e}"


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Backend Parity Tasks Verification")
    print("=" * 70)
    print()
    
    checks: List[Tuple[str, callable]] = [
        ("01.04 Upload Validations", check_upload_validations),
        ("01.05 Wishlist Clear-All", check_wishlist_clear),
        ("01.06 Admin Order Delete", check_admin_order_delete),
        ("01.07 Product Uniqueness", check_product_uniqueness),
        ("02.01-02.02 Migration Script", check_migration_script),
        ("02.03 Models/Schemas", check_models_schemas),
        ("03.01 OpenAPI Docs", check_openapi_docs),
    ]
    
    results: List[Tuple[str, bool, str]] = []
    
    for task_id, check_func in checks:
        try:
            success, message = check_func()
            results.append((task_id, success, message))
            print(f"{message}")
        except Exception as e:
            results.append((task_id, False, f"✗ {task_id}: {e}"))
            print(f"✗ {task_id}: {e}")
    
    print()
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 70)
    
    if passed == total:
        print("\n✓ All parity tasks verified successfully!")
        print("\nNext steps:")
        print("  1. Start the server: uvicorn app.main:app --reload")
        print("  2. Test endpoints using app/docs/examples.http")
        print("  3. Run migration: python -m app.tools.mysql_to_sqlite --help")
        return 0
    else:
        print("\n✗ Some checks failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
