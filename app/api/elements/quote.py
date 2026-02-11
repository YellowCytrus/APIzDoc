"""
POST/GET/PATCH/PUT /profiles/{profile_id}/quote
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.quote import QuoteStyles, QuoteStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/quote", tags=["quote"])


def _row_to_style(row: ProfileElement) -> QuoteStyles:
    return QuoteStyles(indent=row.quote_indent_em)


def _apply_style(row: ProfileElement, body: QuoteStyles) -> None:
    row.quote_indent_em = body.indent


def _apply_style_update(row: ProfileElement, body: QuoteStylesUpdate) -> None:
    if body.indent is not None:
        row.quote_indent_em = body.indent


@router.post("", response_model=QuoteStyles)
async def set_quote(
    profile_id: int,
    body: QuoteStyles,
    session: AsyncSession = Depends(get_session),
) -> QuoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.quote)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=QuoteStyles)
async def get_quote(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> QuoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.quote)
    if row is None:
        raise HTTPException(status_code=404, detail="Quote styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=QuoteStyles)
async def update_quote(
    profile_id: int,
    body: QuoteStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> QuoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.quote)
    if row is None:
        raise HTTPException(status_code=404, detail="Quote styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=QuoteStyles)
async def replace_quote(
    profile_id: int,
    body: QuoteStyles,
    session: AsyncSession = Depends(get_session),
) -> QuoteStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.quote)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
