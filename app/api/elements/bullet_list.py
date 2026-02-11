"""
POST/GET/PATCH/PUT /profiles/{profile_id}/bullet_list
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import get_element_for_profile, get_or_create_element, get_profile_or_404
from app.database import get_session
from app.models.pydantic.bullet_list import BulletListStyles, BulletListStylesUpdate
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement

router = APIRouter(prefix="/profiles/{profile_id}/bullet_list", tags=["bullet_list"])

_DEFAULT_MARKERS = ["- ", "‣", "–"]


def _row_to_style(row: ProfileElement) -> BulletListStyles:
    return BulletListStyles(
        tight=row.tight,
        marker=[row.marker1, row.marker2, row.marker3],
        indent=row.indent_pt,
        body_indent=row.body_indent_em,
        spacing=row.spacing,
    )


def _apply_style(row: ProfileElement, body: BulletListStyles) -> None:
    row.tight = body.tight
    markers = (body.marker + _DEFAULT_MARKERS)[:3]
    row.marker1 = markers[0]
    row.marker2 = markers[1]
    row.marker3 = markers[2]
    row.indent_pt = body.indent
    row.body_indent_em = body.body_indent
    row.spacing = body.spacing


def _apply_style_update(row: ProfileElement, body: BulletListStylesUpdate) -> None:
    if body.tight is not None:
        row.tight = body.tight
    if body.marker is not None:
        markers = (body.marker + _DEFAULT_MARKERS)[:3]
        row.marker1, row.marker2, row.marker3 = markers[0], markers[1], markers[2]
    if body.indent is not None:
        row.indent_pt = body.indent
    if body.body_indent is not None:
        row.body_indent_em = body.body_indent
    if body.spacing is not None:
        row.spacing = body.spacing


@router.post("", response_model=BulletListStyles)
async def set_bullet_list(
    profile_id: int,
    body: BulletListStyles,
    session: AsyncSession = Depends(get_session),
) -> BulletListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.bullet_list)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.get("", response_model=BulletListStyles)
async def get_bullet_list(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> BulletListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.bullet_list)
    if row is None:
        raise HTTPException(status_code=404, detail="Bullet list styles not set for this profile")
    return _row_to_style(row)


@router.patch("", response_model=BulletListStyles)
async def update_bullet_list(
    profile_id: int,
    body: BulletListStylesUpdate,
    session: AsyncSession = Depends(get_session),
) -> BulletListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_element_for_profile(session, profile_id, ElementType.bullet_list)
    if row is None:
        raise HTTPException(status_code=404, detail="Bullet list styles not set for this profile")
    _apply_style_update(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)


@router.put("", response_model=BulletListStyles)
async def replace_bullet_list(
    profile_id: int,
    body: BulletListStyles,
    session: AsyncSession = Depends(get_session),
) -> BulletListStyles:
    await get_profile_or_404(session, profile_id)
    row = await get_or_create_element(session, profile_id, ElementType.bullet_list)
    _apply_style(row, body)
    await session.flush()
    await session.refresh(row)
    return _row_to_style(row)
