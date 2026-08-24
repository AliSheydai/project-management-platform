import asyncio
import os
import re
import uuid
from pathlib import Path

from app.core.exceptions import BadRequestException

# 25 MB max file size limit
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    "application/pdf",
    "text/plain",
    "application/zip",
    "application/x-zip-compressed",
    "application/json",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


def sanitize_filename(filename: str) -> str:
    """Sanitize original filename to prevent path traversal."""
    base_name = os.path.basename(filename)
    sanitized = re.sub(r"[^\w\.\-]", "_", base_name)
    return sanitized or "attachment"


def validate_file(
    content_type: str,
    file_size: int,
) -> None:
    """Validate content type and file size."""
    if file_size > MAX_FILE_SIZE_BYTES:
        raise BadRequestException(
            message=(
                f"File size {file_size} bytes exceeds max allowed limit "
                f"of {MAX_FILE_SIZE_BYTES} bytes (25MB)."
            )
        )
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise BadRequestException(
            message=(
                f"File type '{content_type}' is not allowed. "
                f"Supported types: images, PDFs, text, zip, docx, json."
            )
        )


class LocalStorageService:
    """Local filesystem storage service for task attachments."""

    def __init__(self, base_dir: str = "uploads") -> None:
        self.base_path = Path(base_dir).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file_bytes: bytes,
        original_filename: str,
    ) -> str:
        """Save file bytes to disk with a collision-free UUID prefix."""
        clean_name = sanitize_filename(original_filename)
        unique_name = f"{uuid.uuid4()}_{clean_name}"
        target_path = self.base_path / unique_name

        await asyncio.to_thread(target_path.write_bytes, file_bytes)

        return unique_name

    def get_absolute_path(self, relative_path: str) -> Path:
        """Resolve absolute path and ensure it remains inside the base directory."""
        target_path = (self.base_path / relative_path).resolve()
        if not target_path.is_relative_to(self.base_path):
            raise BadRequestException(message="Invalid file path")
        return target_path

    def delete_file(self, relative_path: str) -> None:
        """Remove physical file from disk if it exists."""
        try:
            target_path = self.get_absolute_path(relative_path)
            if target_path.is_file():
                target_path.unlink()
        except Exception:
            # Tolerant on missing/already deleted files
            pass


# Default singleton instance
storage_service = LocalStorageService()
