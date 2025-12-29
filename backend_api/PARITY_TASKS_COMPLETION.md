# Backend Parity Tasks - Completion Report

This document confirms the completion of all remaining backend parity tasks (01.04–03.01) for the FastAPI migration.

- 01.04 Upload validations: complete (MIME + 5MB + safe filenames; 413/415)
- 01.05 Wishlist clear-all: complete (DELETE /wishlist, 204 idempotent)
- 01.06 Admin order deletion: complete (DELETE /admin/orders/{id}, 409 on restricted)
- 01.07 Product name uniqueness: complete (unique constraint + 409 on conflicts)
- 02.01 MySQL→SQLite migration script: complete (dry-run/execute, reports)
- 02.02 Data transformation helpers: complete (address, items, images, pricing)
- 02.03 Extend models/schemas: complete (Message, Address, ProductImage, OrderItem)
- 03.01 Update API docs/examples: complete (examples.http, README curl)

Please use app/docs/examples.http and README for smoke verification steps.
