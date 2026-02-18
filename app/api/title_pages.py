"""
CRUD для титульных страниц: POST/GET/PATCH/DELETE /title-pages.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.deps import get_title_page_repository
from app.models.pydantic.title_page import TitlePageCreate, TitlePageRead, TitlePageUpdate
from app.models.sqlalchemy.title_page import TitlePage
from app.repositories.title_page_repository import TitlePageRepository

router = APIRouter(prefix="/title-pages", tags=["title-pages"])


def _to_read(page: TitlePage) -> TitlePageRead:
    return TitlePageRead(
        id=page.id,
        name=page.name,
        content=page.content,
        created_at=page.created_at,
    )


@router.post("", response_model=TitlePageRead)
async def create_title_page(
    body: TitlePageCreate,
    repo: TitlePageRepository = Depends(get_title_page_repository),
) -> TitlePageRead:
    page = await repo.create(body.name, body.content.model_dump())
    return _to_read(page)


@router.get("", response_model=list[TitlePageRead])
async def list_title_pages(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo: TitlePageRepository = Depends(get_title_page_repository),
) -> list[TitlePageRead]:
    pages = await repo.list(limit=limit, offset=offset)
    return [_to_read(p) for p in pages]


@router.get("/{title_page_id}", response_model=TitlePageRead)
async def get_title_page(
    title_page_id: int,
    repo: TitlePageRepository = Depends(get_title_page_repository),
) -> TitlePageRead:
    page = await repo.get_by_id(title_page_id)
    if page is None:
        raise HTTPException(status_code=404, detail="Title page not found")
    return _to_read(page)


@router.patch("/{title_page_id}", response_model=TitlePageRead)
async def update_title_page(
    title_page_id: int,
    body: TitlePageUpdate,
    repo: TitlePageRepository = Depends(get_title_page_repository),
) -> TitlePageRead:
    content = body.content.model_dump() if body.content else None
    page = await repo.update(title_page_id, body.name, content)
    if page is None:
        raise HTTPException(status_code=404, detail="Title page not found")
    return _to_read(page)


@router.delete("/{title_page_id}", status_code=204)
async def delete_title_page(
    title_page_id: int,
    repo: TitlePageRepository = Depends(get_title_page_repository),
) -> None:
    deleted = await repo.delete(title_page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Title page not found")
