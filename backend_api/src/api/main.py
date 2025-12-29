"""
Proxy entrypoint used by preview: uvicorn src.api.main:app

This file ensures the backend_api root is on sys.path so that `app.main` imports
reliably in environments where the working dir may differ and provides a clear
message if dependencies are not installed.
"""

import os
import sys

# Ensure project root (backend_api) is on sys.path for `app.*` imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_root = os.path.abspath(os.path.join(_current_dir, "..", ".."))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

try:
    from app.main import app as _app  # re-export under local name to satisfy linter
except Exception as exc:
    raise RuntimeError(
        "Failed to import FastAPI app from app.main. This often means required "
        "packages are not installed in the active virtual environment or the "
        "working directory is not backend_api.\n\n"
        "Fix:\n"
        "  1) Activate your venv\n"
        "  2) pip install -r requirements.txt\n"
        "  3) cd backend_api\n"
        "Then run:\n"
        "  uvicorn src.api.main:app --host 0.0.0.0 --port 3002\n\n"
        f"Original error: {exc}"
    )

# Re-export the FastAPI app symbol for uvicorn import path
app = _app
__all__ = ["app"]
