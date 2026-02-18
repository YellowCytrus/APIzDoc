"""
CRUD для стилевых профилей: POST/GET/PATCH/DELETE /profiles.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.deps import get_profile_repository
from app.models.pydantic.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.models.sqlalchemy.profile import Profile
from app.repositories.profile_repository import ProfileRepository

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileRead)
async def create_profile(
    body: ProfileCreate,
    repo: ProfileRepository = Depends(get_profile_repository),
) -> Profile:
    return await repo.create(body.name)


@router.get("", response_model=list[ProfileRead])
async def list_profiles(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo: ProfileRepository = Depends(get_profile_repository),
) -> list[Profile]:
    return await repo.list(limit=limit, offset=offset)


@router.get("/{profile_id}", response_model=ProfileRead)
async def get_profile(
    profile_id: int,
    repo: ProfileRepository = Depends(get_profile_repository),
) -> Profile:
    profile = await repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=ProfileRead)
async def update_profile(
    profile_id: int,
    body: ProfileUpdate,
    repo: ProfileRepository = Depends(get_profile_repository),
) -> Profile:
    profile = await repo.update(profile_id, body)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: int,
    repo: ProfileRepository = Depends(get_profile_repository),
) -> None:
    deleted = await repo.delete(profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
