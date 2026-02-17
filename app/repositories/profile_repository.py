"""Profile repository: data access for profiles."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pydantic.profile import ProfileUpdate
from app.models.sqlalchemy.profile import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, profile_id: int) -> Profile | None:
        result = await self._session.execute(select(Profile).where(Profile.id == profile_id))
        return result.scalars().one_or_none()

    async def get_by_id_with_styles(self, profile_id: int) -> Profile | None:
        """Загружает профиль с eager load всех style-связей для генерации PDF."""
        result = await self._session.execute(
            select(Profile)
            .where(Profile.id == profile_id)
            .options(
                selectinload(Profile.bullet_list_style),
                selectinload(Profile.document_style),
                selectinload(Profile.figure_style),
                selectinload(Profile.footnote_style),
                selectinload(Profile.heading_style),
                selectinload(Profile.numbered_list_style),
                selectinload(Profile.outline_style),
                selectinload(Profile.page_style),
                selectinload(Profile.par_style),
                selectinload(Profile.quote_style),
                selectinload(Profile.raw_style),
                selectinload(Profile.strong_style),
                selectinload(Profile.table_style),
                selectinload(Profile.terms_style),
            )
        )
        return result.scalars().one_or_none()

    async def list(self, limit: int, offset: int) -> list[Profile]:
        result = await self._session.execute(
            select(Profile).order_by(Profile.id).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, name: str) -> Profile:
        profile = Profile(name=name)
        self._session.add(profile)
        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def update(self, profile_id: int, data: ProfileUpdate) -> Profile | None:
        profile = await self.get_by_id(profile_id)
        if profile is None:
            return None
        if data.name is not None:
            profile.name = data.name
        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def delete(self, profile_id: int) -> bool:
        profile = await self.get_by_id(profile_id)
        if profile is None:
            return False
        await self._session.delete(profile)
        await self._session.flush()
        return True
