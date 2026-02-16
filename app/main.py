"""
Приложение FastAPI: Markdown → PDF через Typst с настраиваемыми стилевыми профилями.
Сервис конвертации Markdown в PDF (Typst). Тестирование: Swagger UI /docs.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.elements import get_element_routers
from app.api.generate import router as generate_router
from app.api.profiles import router as profiles_router
from app.database import init_db
from app.models.sqlalchemy import Profile, ProfileElement  # noqa: F401 — регистрация ORM для create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # завершение: при необходимости освободить engine


app = FastAPI(
    title="PIZDo — Markdown to PDF (Typst)",
    description="Конвертация Markdown в PDF с настраиваемыми стилевыми профилями. API для профилей и генерации PDF.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles_router)
app.include_router(generate_router)
for element_router in get_element_routers():
    app.include_router(element_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Проверка доступности сервиса."""
    return {"status": "ok"}
