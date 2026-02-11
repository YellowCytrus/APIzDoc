"""
Shared helpers for element routers: load profile, resolve or create element row.
"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sqlalchemy.profile import Profile
from app.models.sqlalchemy.profile_element import ElementType, ProfileElement


async def get_profile_or_404(session: AsyncSession, profile_id: int) -> Profile:
    result = await session.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalars().one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


async def get_element_for_profile(
    session: AsyncSession,
    profile_id: int,
    element_type: ElementType,
) -> ProfileElement | None:
    result = await session.execute(
        select(ProfileElement).where(
            ProfileElement.profile_id == profile_id,
            ProfileElement.element_type == element_type,
        )
    )
    return result.scalars().one_or_none()


async def get_or_create_element(
    session: AsyncSession,
    profile_id: int,
    element_type: ElementType,
) -> ProfileElement:
    elem = await get_element_for_profile(session, profile_id, element_type)
    if elem is not None:
        return elem
    elem = ProfileElement(profile_id=profile_id, element_type=element_type)
    session.add(elem)
    await session.flush()
    await session.refresh(elem)
    return elem
