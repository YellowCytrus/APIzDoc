"""FastAPI dependency factories for repositories."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.profile_repository import ProfileRepository
from app.repositories.title_page_repository import TitlePageRepository


async def get_profile_repository(
    session: AsyncSession = Depends(get_session),
) -> ProfileRepository:
    return ProfileRepository(session)


async def get_title_page_repository(
    session: AsyncSession = Depends(get_session),
) -> TitlePageRepository:
    return TitlePageRepository(session)
