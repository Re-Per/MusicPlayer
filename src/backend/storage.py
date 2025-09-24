"""Backend: File storage helpers for uploaded audio."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import BinaryIO

from ..config import UPLOADS_DIR


AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".flac", ".ogg"}


def _resolve_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def generate_filename(original_name: str) -> str:
    """Return a unique filename preserving the original extension."""
    extension = _resolve_extension(original_name)
    if not extension:
        extension = ".bin"
    unique_id = uuid.uuid4().hex
    return f"{unique_id}{extension}"


def save_file(upload_stream: BinaryIO, destination_name: str) -> Path:
    """Persist the uploaded file stream into the uploads directory."""
    destination_path = UPLOADS_DIR / destination_name
    with destination_path.open("wb") as output:
        shutil.copyfileobj(upload_stream, output)
    return destination_path


def is_supported_audio(filename: str) -> bool:
    """Check whether the file has a supported audio extension."""
    return _resolve_extension(filename) in AUDIO_EXTENSIONS
