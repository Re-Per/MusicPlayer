"""Backend: FastAPI application managing uploads and metadata."""
from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, File, HTTPException, UploadFile

from .database import DatabaseManager, UploadRecord
from .storage import generate_filename, is_supported_audio, save_file


def create_app() -> FastAPI:
    """Configure and return the FastAPI application instance."""
    app = FastAPI(title="StreamFusion Prototype API", version="0.1.0")
    database = DatabaseManager()

    @app.post("/upload")
    async def upload_audio(file: UploadFile = File(...)) -> dict:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename.")
        if not is_supported_audio(file.filename):
            raise HTTPException(status_code=400, detail="Unsupported audio format.")

        stored_name = generate_filename(file.filename)
        file.file.seek(0)
        saved_path = save_file(file.file, stored_name)

        record = UploadRecord(
            stored_name=stored_name,
            original_name=file.filename,
            file_size=saved_path.stat().st_size,
            file_format=saved_path.suffix.lstrip("."),
            uploaded_at=datetime.utcnow(),
        )
        database.insert_upload(record)

        return {
            "message": "Upload Successful",
            "stored_name": record.stored_name,
            "original_name": record.original_name,
            "file_size": record.file_size,
            "file_format": record.file_format,
            "uploaded_at": record.uploaded_at.isoformat(),
        }

    @app.get("/list-songs")
    async def list_songs() -> dict:
        uploads = database.list_uploads()
        return {
            "items": [
                {
                    "stored_name": item.stored_name,
                    "original_name": item.original_name,
                    "file_size": item.file_size,
                    "file_format": item.file_format,
                    "uploaded_at": item.uploaded_at.isoformat(),
                }
                for item in uploads
            ]
        }

    @app.on_event("shutdown")
    def shutdown() -> None:
        database.close()

    return app
