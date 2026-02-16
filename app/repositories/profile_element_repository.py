"""Profile element repository: data access for profile element styles."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sqlalchemy.profile_element import ElementType, ProfileElement


class ProfileElementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_profile_and_type(
        self,
        profile_id: int,
        element_type: ElementType,
    ) -> ProfileElement | None:
        result = await self._session.execute(
            select(ProfileElement).where(
                ProfileElement.profile_id == profile_id,
                ProfileElement.element_type == element_type,
            )
        )
        return result.scalars().one_or_none()

    async def get_or_create(
        self,
        profile_id: int,
        element_type: ElementType,
    ) -> ProfileElement:
        elem = await self.get_by_profile_and_type(profile_id, element_type)
        if elem is not None:
            return elem
        elem = ProfileElement(profile_id=profile_id, element_type=element_type)
        self._session.add(elem)
        await self._session.flush()
        await self._session.refresh(elem)
        return elem

    async def persist(self, elem: ProfileElement) -> None:
        """Flush and refresh the element after modifications."""
        await self._session.flush()
        await self._session.refresh(elem)
