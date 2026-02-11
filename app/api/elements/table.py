"""
POST/GET/PATCH/PUT /profiles/{profile_id}/table
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.table import TableStyles, TableStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/table", tags=["table"])


def _row_to_style(row: ProfileElement) -> TableStyles:
    return TableStyles(stroke=row.table_stroke)


def _apply_style(row: ProfileElement, body: TableStyles) -> None:
    row.table_stroke = body.stroke


def _apply_style_update(row: ProfileElement, body: TableStylesUpdate) -> None:
    if body.stroke is not None:
        row.table_stroke = body.stroke


@router.post("", response_model=TableStyles)
async def set_table(
    profile_id: int,
    body: TableStyles,
    session: AsyncSession = Depends(get_session),
) -> TableStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.table)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=TableStyles)
async def get_table(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> TableStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.table)
    if row is None:
        raise HTTPException(status_code=404, detail="Table styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=TableStyles)
async def update_table(
    profile_id: int,
    body: TableStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> TableStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.table)
    if row is None:
        raise HTTPException(status_code=404, detail="Table styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=TableStyles)
async def replace_table(
    profile_id: int,
    body: TableStyles,
    session: AsyncSession = Depends(get_session),
) -> TableStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.table)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
