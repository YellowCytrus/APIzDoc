"""
POST/GET/PATCH/PUT /profiles/{profile_id}/numbered_list
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.numbered_list import NumberedListStyles, NumberedListStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/numbered_list", tags=["numbered_list"])


def _row_to_style(row: ProfileElement) -> NumberedListStyles:
    return NumberedListStyles(
        tight=row.tight,
        indent=row.indent_pt,
        body_indent=row.body_indent_em,
        spacing=row.spacing,
    )


def _apply_style(row: ProfileElement, body: NumberedListStyles) -> None:
    row.tight = body.tight
    row.indent_pt = body.indent
    row.body_indent_em = body.body_indent
    row.spacing = body.spacing


def _apply_style_update(row: ProfileElement, body: NumberedListStylesUpdate) -> None:
    if body.tight is not None:
        row.tight = body.tight
    if body.indent is not None:
        row.indent_pt = body.indent
    if body.body_indent is not None:
        row.body_indent_em = body.body_indent
    if body.spacing is not None:
        row.spacing = body.spacing


@router.post("", response_model=NumberedListStyles)
async def set_numbered_list(
    profile_id: int,
    body: NumberedListStyles,
    session: AsyncSession = Depends(get_session),
) -> NumberedListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.numbered_list)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=NumberedListStyles)
async def get_numbered_list(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> NumberedListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.numbered_list)
    if row is None:
        raise HTTPException(status_code=404, detail="Numbered list styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=NumberedListStyles)
async def update_numbered_list(
    profile_id: int,
    body: NumberedListStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> NumberedListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.numbered_list)
    if row is None:
        raise HTTPException(status_code=404, detail="Numbered list styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=NumberedListStyles)
async def replace_numbered_list(
    profile_id: int,
    body: NumberedListStyles,
    session: AsyncSession = Depends(get_session),
) -> NumberedListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.numbered_list)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
