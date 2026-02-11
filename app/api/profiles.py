"""
CRUD for style profiles: POST/GET/PATCH/DELETE /profiles.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.pydantic.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.models.sqlalchemy.profile import Profile

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileRead)
async def create_profile(
    body: ProfileCreate,
    session: AsyncSession = Depends(get_session),
) -> Profile:
    profile = Profile(name=body.name)
    session.add(profile)
    await session.flush()
    await session.refresh(profile)
    return profile


@router.get("", response_model=list[ProfileRead])
async def list_profiles(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[Profile]:
    result = await session.execute(
        select(Profile).order_by(Profile.id).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


@router.get("/{profile_id}", response_model=ProfileRead)
async def get_profile(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> Profile:
    result = await session.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalars().one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=ProfileRead)
async def update_profile(
    profile_id: int,
    body: ProfileUpdate,
    session: AsyncSession = Depends(get_session),
) -> Profile:
    result = await session.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalars().one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if body.name is not None:
        profile.name = body.name
    await session.flush()
    await session.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    result = await session.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalars().one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    await session.delete(profile)
    await session.flush()
