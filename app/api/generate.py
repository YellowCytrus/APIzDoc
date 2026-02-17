"""
POST /profiles/{profile_id}/generate-pdf — загрузка Markdown, возврат PDF.
GET  /profiles/{profile_id}/preamble     — текст преамбулы Typst.
"""
import logging
from pathlib import PurePosixPath
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse, Response

from app.deps import get_profile_repository
from app.repositories.profile_repository import ProfileRepository
from app.utils.pandoc_converter import PandocError, markdown_to_typst
from app.utils.typst_compiler import TypstCompileError, compile_typst_to_pdf
from app.utils.typst_preamble import build_typst_preamble

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["generate"])

_ALLOWED_CONTENT_TYPES = {"text/markdown", "text/plain", "application/octet-stream"}
_ALLOWED_EXTENSIONS = {".md", ".markdown", ".txt"}
_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.get("/{profile_id}/preamble", response_class=PlainTextResponse)
async def get_preamble(
    profile_id: int,
    repo: ProfileRepository = Depends(get_profile_repository),
) -> PlainTextResponse:
    """Возвращает текст преамбулы Typst #set для данного профиля."""
    profile = await repo.get_by_id_with_styles(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return PlainTextResponse(build_typst_preamble(profile))


@router.post("/{profile_id}/generate-pdf", response_class=Response)
async def generate_pdf(
    profile_id: int,
    file: UploadFile,
    repo: ProfileRepository = Depends(get_profile_repository),
) -> Response:
    """
    Загрузка Markdown-файла; конвертация в Typst со стилями профиля и компиляция в PDF.
    Возвращает байты PDF с Content-Disposition attachment.
    """
    profile = await repo.get_by_id_with_styles(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    ext = PurePosixPath(file.filename or "").suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")
    if file.content_type:
        base_type = file.content_type.split(";")[0].strip().lower()
        if base_type not in _ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported content type")

    content = await file.read()
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty Markdown file")

    try:
        typst_body = await markdown_to_typst(content)
    except PandocError as e:
        logger.exception("Pandoc failed: %s", e.stderr)
        raise HTTPException(status_code=500, detail="Markdown conversion failed") from e

    preamble = build_typst_preamble(profile)
    full_typst = preamble + "\n" + typst_body

    try:
        pdf_bytes = await compile_typst_to_pdf(full_typst)
    except TypstCompileError as e:
        logger.exception("Typst compile failed: %s", e.stderr)
        raise HTTPException(status_code=500, detail="PDF compilation failed") from e

    filename = file.filename or "document.md"
    pdf_name = filename.rsplit(".", 1)[0] + ".pdf" if "." in filename else "document.pdf"
    safe_ascii = pdf_name.encode("ascii", errors="replace").decode("ascii")
    disp = f'attachment; filename="{safe_ascii}"'
    if pdf_name != safe_ascii:
        disp += f"; filename*=UTF-8''{quote(pdf_name, safe='.')}"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": disp},
    )
