"""
POST /profiles/{profile_id}/generate-pdf — upload Markdown, return PDF.
"""
import logging
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models.sqlalchemy.profile import Profile
from app.models.sqlalchemy.profile_element import ProfileElement
from app.utils.pandoc_converter import PandocError, markdown_to_typst
from app.utils.typst_compiler import TypstCompileError, compile_typst_to_pdf
from app.utils.typst_preamble import build_typst_preamble
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["generate"])


@router.post("/{profile_id}/generate-pdf", response_class=Response)
async def generate_pdf(
    profile_id: int,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """
    Upload a Markdown file; convert to Typst with profile styles and compile to PDF.
    Returns PDF bytes with Content-Disposition attachment.
    """
    result = await session.execute(
        select(Profile).where(Profile.id == profile_id).options(selectinload(Profile.elements))
    )
    profile = result.scalars().one_or_none()
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
