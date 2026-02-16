"""
POST /profiles/{profile_id}/generate-pdf — загрузка Markdown, возврат PDF.
"""
import logging
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response

from app.deps import get_profile_repository
from app.repositories.profile_repository import ProfileRepository
from app.utils.pandoc_converter import PandocError, markdown_to_typst
from app.utils.typst_compiler import TypstCompileError, compile_typst_to_pdf
from app.utils.typst_preamble import build_typst_preamble

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["generate"])


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
    profile = await repo.get_by_id_with_elements(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    content = await file.read()
    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty Markdown file")

    try:
        typst_body = await markdown_to_typst(content)
    except PandocError as e:
        logger.exception("Pandoc failed: %s", e.stderr)
        raise HTTPException(status_code=500, detail=f"Pandoc failed: {e!s}") from e

    preamble = build_typst_preamble(profile.elements)
    full_typst = preamble + "\n" + typst_body

    try:
        pdf_bytes = await compile_typst_to_pdf(full_typst)
    except TypstCompileError as e:
        logger.exception("Typst compile failed: %s", e.stderr)
        raise HTTPException(status_code=500, detail=f"Typst compilation failed: {e!s}") from e

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
