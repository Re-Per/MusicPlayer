"""Configuration utilities for StreamFusion prototype."""
from pathlib import Path
import sys


def _resolve_base_dir() -> Path:
    """Return base directory for assets, aware of PyInstaller bundles."""
    if getattr(sys, "frozen", False):  # Running inside PyInstaller bundle
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = _resolve_base_dir()
UPLOADS_DIR = BASE_DIR / "uploads"
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "streamfusion.db"
API_HOST = "127.0.0.1"
API_PORT = 8765

for directory in (UPLOADS_DIR, DB_DIR):
    directory.mkdir(parents=True, exist_ok=True)
