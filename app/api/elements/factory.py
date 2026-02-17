"""
Фабрика роутеров элементов: генерирует POST/GET/PATCH/PUT из ElementDescriptor.
Generic маппинг ORM <-> DTO через model_validate / model_dump.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.elements.common import ElementDescriptor
from app.database import get_session
from app.deps import get_profile_repository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.style_repository import StyleRepository


def create_element_router(descriptor: ElementDescriptor[Any, Any, Any]) -> APIRouter:
    """
    Создаёт APIRouter с POST/GET/PATCH/PUT для данного типа элемента.
    """
    router = APIRouter(
        prefix=f"/profiles/{{profile_id}}/{descriptor.path}",
        tags=[descriptor.tag],
    )
    orm_model = descriptor.orm_model
    styles_model = descriptor.styles_model
    styles_update_model = descriptor.styles_update_model

    @router.post("", response_model=styles_model)
    async def post_element(
        profile_id: int,
        body: styles_model,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        style_repo: StyleRepository[Any] = StyleRepository(session, orm_model)
        row = await style_repo.get_or_create(profile_id)
        for key, value in body.model_dump().items():
            setattr(row, key, value)
        await style_repo.persist(row)
        return styles_model.model_validate(row, from_attributes=True)

    @router.get("", response_model=styles_model)
    async def get_element(
        profile_id: int,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        style_repo: StyleRepository[Any] = StyleRepository(session, orm_model)
        row = await style_repo.get_or_create(profile_id)
        return styles_model.model_validate(row, from_attributes=True)

    @router.patch("", response_model=styles_model)
    async def patch_element(
        profile_id: int,
        body: styles_update_model,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        style_repo: StyleRepository[Any] = StyleRepository(session, orm_model)
        row = await style_repo.get_by_profile_id(profile_id)
        if row is None:
            raise HTTPException(status_code=404, detail=descriptor.not_found_detail)
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(row, key, value)
        await style_repo.persist(row)
        return styles_model.model_validate(row, from_attributes=True)

    @router.put("", response_model=styles_model)
    async def put_element(
        profile_id: int,
        body: styles_model,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        style_repo: StyleRepository[Any] = StyleRepository(session, orm_model)
        row = await style_repo.get_or_create(profile_id)
        for key, value in body.model_dump().items():
            setattr(row, key, value)
        await style_repo.persist(row)
        return styles_model.model_validate(row, from_attributes=True)

    return router
