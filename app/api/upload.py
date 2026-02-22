"""
POST /upload-image — загрузка изображения в локальное хранилище проекта.
Изображения сохраняются в ./images/ с именем {uuid}.{ext}.
"""

import logging
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

logger = logging.getLogger(__name__)

router = APIRouter(tags=["upload"])

# Разрешить только изображения
_ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
_ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}
_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Папка images относительно корня проекта (работает и в Docker с volume ./images:/app/images)
IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "images"


def _ensure_images_dir() -> Path:
    """Создаёт папку images, если её нет."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    return IMAGES_DIR


def _safe_filename(ext: str) -> str:
    """Генерирует безопасное имя файла: UUID + расширение."""
    ext_lower = ext.lower()
    if ext_lower not in _ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported extension: {ext}")
    return f"{uuid.uuid4().hex}{ext_lower}"


def _validate_no_path_traversal(filename: str) -> None:
    """Запрет path traversal в имени файла."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError("Path traversal not allowed")


@router.post("/upload-image")
async def upload_image(file: UploadFile) -> dict[str, str]:
    """
    Загружает изображение в локальное хранилище.
    Возвращает {"path": "images/uuid.ext"} для вставки в Markdown.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    # Проверка расширения
    ext_match = re.search(r"\.([a-zA-Z0-9]+)$", file.filename)
    ext = f".{ext_match.group(1).lower()}" if ext_match else ""
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported extension. Allowed: {', '.join(_ALLOWED_EXTENSIONS)}",
        )

    # Проверка MIME-типа
    if file.content_type:
        base_type = file.content_type.split(";")[0].strip().lower()
        if base_type not in _ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported content type")

    content = await file.read()
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {_MAX_FILE_SIZE // (1024*1024)} MB)",
        )

    safe_name = _safe_filename(ext)
    _validate_no_path_traversal(safe_name)

    images_dir = _ensure_images_dir()
    target_path = images_dir / safe_name
    target_path.write_bytes(content)

    # Относительный путь для Markdown: images/uuid.ext
    path = f"images/{safe_name}"
    logger.info("Uploaded image: %s", path)
    return {"path": path}
