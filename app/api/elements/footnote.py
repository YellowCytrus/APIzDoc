"""
POST/GET/PATCH/PUT /profiles/{profile_id}/footnote
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.footnote import FootnoteStyles, FootnoteStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/footnote", tags=["footnote"])


def _row_to_style(row: ProfileElement) -> FootnoteStyles:
    return FootnoteStyles(marker_format=row.footnote_marker_fmt)


def _apply_style(row: ProfileElement, body: FootnoteStyles) -> None:
    row.footnote_marker_fmt = body.marker_format


def _apply_style_update(row: ProfileElement, body: FootnoteStylesUpdate) -> None:
    if body.marker_format is not None:
        row.footnote_marker_fmt = body.marker_format


@router.post("", response_model=FootnoteStyles)
async def set_footnote(
    profile_id: int,
    body: FootnoteStyles,
    session: AsyncSession = Depends(get_session),
) -> FootnoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.footnote)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=FootnoteStyles)
async def get_footnote(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> FootnoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.footnote)
    if row is None:
        raise HTTPException(status_code=404, detail="Footnote styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=FootnoteStyles)
async def update_footnote(
    profile_id: int,
    body: FootnoteStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> FootnoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.footnote)
    if row is None:
        raise HTTPException(status_code=404, detail="Footnote styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=FootnoteStyles)
async def replace_footnote(
    profile_id: int,
    body: FootnoteStyles,
    session: AsyncSession = Depends(get_session),
) -> FootnoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.footnote)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
