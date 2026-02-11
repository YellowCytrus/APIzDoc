"""
POST/GET/PATCH/PUT /profiles/{profile_id}/figure
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.figure import FigureStyles, FigureStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/figure", tags=["figure"])


def _row_to_style(row: ProfileElement) -> FigureStyles:
    return FigureStyles(
        width=row.figure_width_em,
        height=row.figure_height_em,
    )


def _apply_style(row: ProfileElement, body: FigureStyles) -> None:
    row.figure_width_em = body.width
    row.figure_height_em = body.height


def _apply_style_update(row: ProfileElement, body: FigureStylesUpdate) -> None:
    if body.width is not None:
        row.figure_width_em = body.width
    if body.height is not None:
        row.figure_height_em = body.height


@router.post("", response_model=FigureStyles)
async def set_figure(
    profile_id: int,
    body: FigureStyles,
    session: AsyncSession = Depends(get_session),
) -> FigureStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.figure)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=FigureStyles)
async def get_figure(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> FigureStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.figure)
    if row is None:
        raise HTTPException(status_code=404, detail="Figure styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=FigureStyles)
async def update_figure(
    profile_id: int,
    body: FigureStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> FigureStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.figure)
    if row is None:
        raise HTTPException(status_code=404, detail="Figure styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=FigureStyles)
async def replace_figure(
    profile_id: int,
    body: FigureStyles,
    session: AsyncSession = Depends(get_session),
) -> FigureStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.figure)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
