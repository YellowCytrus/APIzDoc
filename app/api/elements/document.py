"""
POST/GET/PATCH/PUT /profiles/{profile_id}/document
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.document import DocumentStyles, DocumentStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/document", tags=["document"])


def _row_to_style(row: ProfileElement) -> DocumentStyles:
    return DocumentStyles(
        font_size=row.font_size_pt,
        line_spacing=row.line_spacing_em,
    )


def _apply_style(row: ProfileElement, body: DocumentStyles) -> None:
    row.font_size_pt = body.font_size
    row.line_spacing_em = body.line_spacing


def _apply_style_update(row: ProfileElement, body: DocumentStylesUpdate) -> None:
    if body.font_size is not None:
        row.font_size_pt = body.font_size
    if body.line_spacing is not None:
        row.line_spacing_em = body.line_spacing


@router.post("", response_model=DocumentStyles)
async def set_document(
    profile_id: int,
    body: DocumentStyles,
    session: AsyncSession = Depends(get_session),
) -> DocumentStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.document)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=DocumentStyles)
async def get_document(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> DocumentStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.document)
    if row is None:
        raise HTTPException(status_code=404, detail="Document styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=DocumentStyles)
async def update_document(
    profile_id: int,
    body: DocumentStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> DocumentStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.document)
    if row is None:
        raise HTTPException(status_code=404, detail="Document styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=DocumentStyles)
async def replace_document(
    profile_id: int,
    body: DocumentStyles,
    session: AsyncSession = Depends(get_session),
) -> DocumentStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.document)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
