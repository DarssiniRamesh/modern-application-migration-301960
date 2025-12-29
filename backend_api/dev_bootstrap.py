#!/usr/bin/env python3
"""
Lightweight bootstrap to ensure dependencies are installed before starting the FastAPI app.

This is intended for preview environments that may launch uvicorn without running pip install first.
It will:
- Attempt to import critical dependencies.
- If import fails, run: pip install -r requirements.txt (user install where appropriate).
- Optionally start uvicorn if RUN_SERVER=1 is set.

Usage:
  python dev_bootstrap.py             # just ensure deps
  RUN_SERVER=1 HOST=0.0.0.0 PORT=3002 python dev_bootstrap.py  # ensure deps then start server
"""
import os
import subprocess
import sys


REQUIREMENTS_FILE = os.path.join(os.path.dirname(__file__), "requirements.txt")
PROJECT_ROOT = os.path.dirname(__file__)


def _needs_install() -> bool:
    """Return True if critical imports fail."""
    try:
        import sqlalchemy  # noqa: F401
        import fastapi  # noqa: F401
        import jose  # noqa: F401
        import passlib  # noqa: F401
        return False
    except Exception:
        return True


def _pip_install() -> int:
    """Run pip install -r requirements.txt in a non-interactive way."""
    print("[bootstrap] Installing dependencies from requirements.txt ...", flush=True)
    cmd = [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE]
    # Prefer user install to avoid permission issues
    env = os.environ.copy()
    env.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, check=False)
        return result.returncode
    except Exception as exc:
        print(f"[bootstrap] pip install failed: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    if _needs_install():
        code = _pip_install()
        if code != 0:
            print("[bootstrap] Dependency installation failed.", file=sys.stderr)
            return code
        # Re-check
        if _needs_install():
            print("[bootstrap] Critical imports still failing after install.", file=sys.stderr)
            return 2

    print("[bootstrap] Dependencies OK.", flush=True)

    if os.getenv("RUN_SERVER") == "1":
        host = os.getenv("HOST", "0.0.0.0")
        port = os.getenv("PORT", "3002")
        # Start uvicorn for either legacy or current entrypoint
        target = os.getenv("UVICORN_TARGET", "app.main:app")
        cmd = [sys.executable, "-m", "uvicorn", target, "--host", host, "--port", port]
        print(f"[bootstrap] Starting server: {' '.join(cmd)}", flush=True)
        return subprocess.call(cmd)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
