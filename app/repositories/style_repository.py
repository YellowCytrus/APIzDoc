"""Generic style repository: data access for any per-profile style table."""
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class StyleRepository(Generic[T]):
    """CRUD для любой style-модели с уникальным profile_id."""

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self._session = session
        self._model = model

    async def get_by_profile_id(self, profile_id: int) -> T | None:
        result = await self._session.execute(
            select(self._model).where(self._model.profile_id == profile_id)  # type: ignore[attr-defined]
        )
        return result.scalars().one_or_none()

    async def get_or_create(self, profile_id: int) -> T:
        entity = await self.get_by_profile_id(profile_id)
        if entity is not None:
            return entity
        entity = self._model(profile_id=profile_id)  # type: ignore[call-arg]
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def persist(self, entity: T) -> None:
        """Flush и refresh после модификаций."""
        await self._session.flush()
        await self._session.refresh(entity)
