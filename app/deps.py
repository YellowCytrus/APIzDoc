"""FastAPI dependency factories for repositories."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.profile_element_repository import ProfileElementRepository
from app.repositories.profile_repository import ProfileRepository


async def get_profile_repository(
    session: AsyncSession = Depends(get_session),
) -> ProfileRepository:
    return ProfileRepository(session)


async def get_profile_element_repository(
    session: AsyncSession = Depends(get_session),
) -> ProfileElementRepository:
    return ProfileElementRepository(session)
