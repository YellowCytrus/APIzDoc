"""
FastAPI app: Markdown → PDF via Typst with customizable style profiles.
Сервис конвертации Markdown в PDF (Typst). Тестирование: Swagger UI /docs.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.elements import bullet_list, document, figure, footnote, heading, numbered_list, par, quote, table
from app.api.generate import router as generate_router
from app.api.profiles import router as profiles_router
from app.database import init_db
from app.models.sqlalchemy import Profile, ProfileElement  # noqa: F401 — register ORM for create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # shutdown: engine dispose if needed


app = FastAPI(
    title="PIZDo — Markdown to PDF (Typst)",
    description="Конвертация Markdown в PDF с настраиваемыми стилевыми профилями. API для профилей и генерации PDF.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(profiles_router)
app.include_router(generate_router)
app.include_router(bullet_list.router)
app.include_router(document.router)
app.include_router(figure.router)
app.include_router(footnote.router)
app.include_router(heading.router)
app.include_router(numbered_list.router)
app.include_router(par.router)
app.include_router(quote.router)
app.include_router(table.router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Проверка доступности сервиса."""
    return {"status": "ok"}
