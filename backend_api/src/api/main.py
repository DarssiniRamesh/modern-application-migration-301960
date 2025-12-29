# Deprecated: main app now lives at app/main.py
# This file remains to satisfy historical tooling but is no longer used to start the server.
from app.main import app as _app  # noqa: F401
# Re-export to keep old import paths working
app = _app
