"""
POST/GET/PATCH/PUT /profiles/{profile_id}/par
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.par import ParStyles, ParStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/par", tags=["par"])


def _row_to_style(row: ProfileElement) -> ParStyles:
    return ParStyles(spacing=row.spacing_em)


def _apply_style(row: ProfileElement, body: ParStyles) -> None:
    row.spacing_em = body.spacing


def _apply_style_update(row: ProfileElement, body: ParStylesUpdate) -> None:
    if body.spacing is not None:
        row.spacing_em = body.spacing


@router.post("", response_model=ParStyles)
async def set_par(
    profile_id: int,
    body: ParStyles,
    session: AsyncSession = Depends(get_session),
) -> ParStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.par)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=ParStyles)
async def get_par(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> ParStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.par)
    if row is None:
        raise HTTPException(status_code=404, detail="Par styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=ParStyles)
async def update_par(
    profile_id: int,
    body: ParStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> ParStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.par)
    if row is None:
        raise HTTPException(status_code=404, detail="Par styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=ParStyles)
async def replace_par(
    profile_id: int,
    body: ParStyles,
    session: AsyncSession = Depends(get_session),
) -> ParStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.par)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
