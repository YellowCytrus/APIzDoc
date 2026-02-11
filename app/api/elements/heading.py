"""
POST/GET/PATCH/PUT /profiles/{profile_id}/heading
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.heading import HeadingStyles, HeadingStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/heading", tags=["heading"])


def _row_to_style(row: ProfileElement) -> HeadingStyles:
    return HeadingStyles(numbering=row.heading_numbering)


def _apply_style(row: ProfileElement, body: HeadingStyles) -> None:
    row.heading_numbering = body.numbering


def _apply_style_update(row: ProfileElement, body: HeadingStylesUpdate) -> None:
    if body.numbering is not None:
        row.heading_numbering = body.numbering


@router.post("", response_model=HeadingStyles)
async def set_heading(
    profile_id: int,
    body: HeadingStyles,
    session: AsyncSession = Depends(get_session),
) -> HeadingStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.heading)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=HeadingStyles)
async def get_heading(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> HeadingStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.heading)
    if row is None:
        raise HTTPException(status_code=404, detail="Heading styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=HeadingStyles)
async def update_heading(
    profile_id: int,
    body: HeadingStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> HeadingStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.heading)
    if row is None:
        raise HTTPException(status_code=404, detail="Heading styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=HeadingStyles)
async def replace_heading(
    profile_id: int,
    body: HeadingStyles,
    session: AsyncSession = Depends(get_session),
) -> HeadingStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.heading)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
