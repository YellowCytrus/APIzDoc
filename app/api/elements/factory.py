"""
Фабрика роутеров элементов: генерирует POST/GET/PATCH/PUT из ElementDescriptor.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.elements.common import ElementDescriptor
from app.deps import get_profile_element_repository, get_profile_repository
from app.repositories.profile_element_repository import ProfileElementRepository
from app.repositories.profile_repository import ProfileRepository


def create_element_router(descriptor: ElementDescriptor[Any, Any]) -> APIRouter:
    """
    Создаёт APIRouter с POST/GET/PATCH/PUT для данного типа элемента.
    """
    router = APIRouter(
        prefix=f"/profiles/{{profile_id}}/{descriptor.path}",
        tags=[descriptor.tag],
    )
    styles_model = descriptor.styles_model
    styles_update_model = descriptor.styles_update_model
    element_type = descriptor.element_type

    @router.post("", response_model=styles_model)
    async def post_element(
        profile_id: int,
        body: styles_model,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        element_repo: ProfileElementRepository = Depends(get_profile_element_repository),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        row = await element_repo.get_or_create(profile_id, element_type)
        descriptor.apply_full(row, body)
        await element_repo.persist(row)
        return descriptor.to_dto(row)

    @router.get("", response_model=styles_model)
    async def get_element(
        profile_id: int,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        element_repo: ProfileElementRepository = Depends(get_profile_element_repository),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        row = await element_repo.get_or_create(profile_id, element_type)
        return descriptor.to_dto(row)

    @router.patch("", response_model=styles_model)
    async def patch_element(
        profile_id: int,
        body: styles_update_model,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        element_repo: ProfileElementRepository = Depends(get_profile_element_repository),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        row = await element_repo.get_by_profile_and_type(profile_id, element_type)
        if row is None:
            raise HTTPException(status_code=404, detail=descriptor.not_found_detail)
        descriptor.apply_partial(row, body)
        await element_repo.persist(row)
        return descriptor.to_dto(row)

    @router.put("", response_model=styles_model)
    async def put_element(
        profile_id: int,
        body: styles_model,
        profile_repo: ProfileRepository = Depends(get_profile_repository),
        element_repo: ProfileElementRepository = Depends(get_profile_element_repository),
    ) -> Any:
        if await profile_repo.get_by_id(profile_id) is None:
            raise HTTPException(status_code=404, detail="Profile not found")
        row = await element_repo.get_or_create(profile_id, element_type)
        descriptor.apply_full(row, body)
        await element_repo.persist(row)
        return descriptor.to_dto(row)

    return router
