"""Frontend: Lightweight HTTP client for the StreamFusion backend."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import requests

from ..config import API_HOST, API_PORT

BASE_URL = f"http://{API_HOST}:{API_PORT}"


def upload_audio(file_path: Path) -> Dict[str, Any]:
    """Upload an audio file to the backend and return the response payload."""
    with file_path.open("rb") as buffer:
        files = {
            "file": (
                file_path.name,
                buffer,
                _guess_mime_type(file_path.suffix),
            )
        }
        response = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
        response.raise_for_status()
        return response.json()


def _guess_mime_type(extension: str) -> str:
    extension = extension.lower()
    if extension == ".mp3":
        return "audio/mpeg"
    if extension == ".wav":
        return "audio/wav"
    if extension == ".flac":
        return "audio/flac"
    if extension == ".aac":
        return "audio/aac"
    if extension == ".ogg":
        return "audio/ogg"
    return "application/octet-stream"
