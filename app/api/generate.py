"""
POST /profiles/{profile_id}/generate-pdf — загрузка Markdown, возврат PDF.
POST /profiles/{profile_id}/export-typ  — загрузка Markdown, возврат полного .typ.
GET  /profiles/{profile_id}/preamble     — текст преамбулы Typst.
"""

import logging
from pathlib import PurePosixPath
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse, Response

from app.deps import get_profile_repository, get_title_page_repository
from app.models.pydantic.page_editor import TitlePageContent
from app.repositories.profile_repository import ProfileRepository
from app.repositories.title_page_repository import TitlePageRepository
from app.api.upload import IMAGES_DIR
from app.utils.pandoc_converter import PandocError, markdown_to_typst
from app.utils.typst_compiler import TypstCompileError, compile_typst_to_pdf
from app.utils.typst_preamble import build_typst_preamble
from app.utils.typst_title_exporter import generate_fragment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["generate"])

_ALLOWED_CONTENT_TYPES = {"text/markdown", "text/plain", "application/octet-stream"}
_ALLOWED_EXTENSIONS = {".md", ".markdown", ".txt"}
_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def _read_and_validate_markdown(file: UploadFile) -> bytes:
    """Read upload, validate, return content or raise HTTPException."""
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
    return content


def _content_disposition_attachment(filename: str) -> str:
    """Build Content-Disposition header value for attachment download."""
    safe_ascii = filename.encode("ascii", errors="replace").decode("ascii")
    disp = f'attachment; filename="{safe_ascii}"'
    if filename != safe_ascii:
        disp += f"; filename*=UTF-8''{quote(filename, safe='.')}"
    return disp


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
    title_page_id: int | None = Query(
        None, description="ID титульной страницы для первой страницы PDF"
    ),
    repo: ProfileRepository = Depends(get_profile_repository),
    title_repo: TitlePageRepository = Depends(get_title_page_repository),
) -> Response:
    """
    Загрузка Markdown-файла; конвертация в Typst со стилями профиля и компиляция в PDF.
    Возвращает байты PDF с Content-Disposition attachment.
    """
    profile = await repo.get_by_id_with_styles(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    content = await _read_and_validate_markdown(file)

    try:
        typst_body = await markdown_to_typst(content)
    except PandocError as e:
        logger.exception("Pandoc failed: %s", e.stderr)
        raise HTTPException(status_code=500, detail="Markdown conversion failed") from e

    preamble = build_typst_preamble(profile)

    parts: list[str] = [preamble]
    if title_page_id is not None:
        title_page = await title_repo.get_by_id(title_page_id)
        if title_page is None:
            raise HTTPException(status_code=404, detail="Title page not found")
        tc = TitlePageContent.model_validate(title_page.content)
        parts.append(
            generate_fragment(
                tc.elements,
                tc.paper,
                tc.variables,
                ignore_document_styles=tc.ignore_document_styles,
            )
        )
    parts.append(typst_body)
    full_typst = "\n".join(parts)

    try:
        pdf_bytes = await compile_typst_to_pdf(full_typst, images_dir=IMAGES_DIR)
    except TypstCompileError as e:
        logger.exception("Typst compile failed: %s", e.stderr)
        raise HTTPException(status_code=500, detail="PDF compilation failed") from e

    filename = file.filename or "document.md"
    pdf_name = filename.rsplit(".", 1)[0] + ".pdf" if "." in filename else "document.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": _content_disposition_attachment(pdf_name)},
    )


@router.post("/{profile_id}/export-typ", response_class=PlainTextResponse)
async def export_typ(
    profile_id: int,
    file: UploadFile,
    title_page_id: int | None = Query(
        None, description="ID титульной страницы для первой страницы .typ"
    ),
    repo: ProfileRepository = Depends(get_profile_repository),
    title_repo: TitlePageRepository = Depends(get_title_page_repository),
) -> PlainTextResponse:
    """
    Загрузка Markdown-файла; конвертация в Typst со стилями профиля.
    Возвращает полный исходник .typ без компиляции в PDF.
    """
    profile = await repo.get_by_id_with_styles(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    content = await _read_and_validate_markdown(file)

    try:
        typst_body = await markdown_to_typst(content)
    except PandocError as e:
        logger.exception("Pandoc failed: %s", e.stderr)
        raise HTTPException(status_code=500, detail="Markdown conversion failed") from e

    preamble = build_typst_preamble(profile)
    parts: list[str] = [preamble]
    if title_page_id is not None:
        title_page = await title_repo.get_by_id(title_page_id)
        if title_page is None:
            raise HTTPException(status_code=404, detail="Title page not found")
        tc = TitlePageContent.model_validate(title_page.content)
        parts.append(
            generate_fragment(
                tc.elements,
                tc.paper,
                tc.variables,
                ignore_document_styles=tc.ignore_document_styles,
            )
        )
    parts.append(typst_body)
    full_typst = "\n".join(parts)

    filename = file.filename or "document.md"
    typ_name = filename.rsplit(".", 1)[0] + ".typ" if "." in filename else "document.typ"
    return PlainTextResponse(
        content=full_typst,
        headers={"Content-Disposition": _content_disposition_attachment(typ_name)},
    )
