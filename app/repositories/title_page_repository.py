"""Title page repository: data access for title pages."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pydantic.page_editor import TitlePageContent
from app.models.sqlalchemy.title_page import TitlePage


class TitlePageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, title_page_id: int) -> TitlePage | None:
        result = await self._session.execute(
            select(TitlePage).where(TitlePage.id == title_page_id)
        )
        return result.scalars().one_or_none()

    async def list(self, limit: int, offset: int) -> list[TitlePage]:
        result = await self._session.execute(
            select(TitlePage).order_by(TitlePage.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, name: str, content: dict) -> TitlePage:
        page = TitlePage(name=name, content=content)
        self._session.add(page)
        await self._session.flush()
        await self._session.refresh(page)
        return page

    async def update(self, title_page_id: int, name: str | None, content: dict | None) -> TitlePage | None:
        page = await self.get_by_id(title_page_id)
        if page is None:
            return None
        if name is not None:
            page.name = name
        if content is not None:
            page.content = content
        await self._session.flush()
        await self._session.refresh(page)
        return page

    async def delete(self, title_page_id: int) -> bool:
        page = await self.get_by_id(title_page_id)
        if page is None:
            return False
        await self._session.delete(page)
        await self._session.flush()
        return True
