"""Backend: Database management utilities for StreamFusion."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import List

from ..config import DB_PATH


@dataclass
class UploadRecord:
    """Represents an uploaded audio file stored in SQLite."""
    stored_name: str
    original_name: str
    file_size: int
    file_format: str
    uploaded_at: datetime


class DatabaseManager:
    """Provides thread-safe access to the SQLite metadata store."""

    def __init__(self) -> None:
        self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._lock = Lock()
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS uploads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stored_name TEXT NOT NULL,
                        original_name TEXT NOT NULL,
                        file_size INTEGER NOT NULL,
                        file_format TEXT NOT NULL,
                        uploaded_at TEXT NOT NULL
                    )
                    """
                )

    def insert_upload(self, record: UploadRecord) -> None:
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO uploads (
                        stored_name,
                        original_name,
                        file_size,
                        file_format,
                        uploaded_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        record.stored_name,
                        record.original_name,
                        record.file_size,
                        record.file_format,
                        record.uploaded_at.isoformat(),
                    ),
                )

    def list_uploads(self) -> List[UploadRecord]:
        with self._lock:
            cursor = self._conn.execute(
                "SELECT stored_name, original_name, file_size, file_format, uploaded_at FROM uploads ORDER BY uploaded_at DESC"
            )
            rows = cursor.fetchall()
        return [
            UploadRecord(
                stored_name=row[0],
                original_name=row[1],
                file_size=row[2],
                file_format=row[3],
                uploaded_at=datetime.fromisoformat(row[4]),
            )
            for row in rows
        ]

    def close(self) -> None:
        with self._lock:
            self._conn.close()
