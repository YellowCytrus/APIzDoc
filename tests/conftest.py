"""
Test configuration: DB override, HTTP client, fixtures.
Set POSTGRES_* env before import so app uses test database.
"""

import os
import subprocess
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Use test DB before any app imports
os.environ.setdefault("POSTGRES_DB", "pizdo_test")
os.environ.setdefault("POSTGRES_HOST", "localhost")

from app.database import Base, get_session
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def _check_db_connection():
    """Check DB availability before running tests."""
    import asyncpg

    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    database = os.environ.get("POSTGRES_DB", "pizdo_test")

    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres",  # Connect to default DB first
            timeout=2,
        )
        await conn.close()

        # Check if test DB exists, create if not
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres",
            timeout=2,
        )
        db_exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", database)
        if not db_exists:
            await conn.execute(f'CREATE DATABASE "{database}"')
        await conn.close()
    except Exception as e:
        pytest.skip(
            f"Postgres недоступен на {host}:{port}. Запустите: docker-compose up -d db\nОшибка: {e}"
        )


@pytest.fixture(scope="session", autouse=True)
def _run_migrations(_check_db_connection):
    """Apply Alembic migrations to test DB so schema matches current models."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=root,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"Миграции не применились к тестовой БД: {result.stderr or result.stdout}")


@pytest.fixture(scope="session", autouse=True)
async def _ensure_schema(_run_migrations):
    """Create any missing tables from ORM (migrations may not create base tables)."""
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()


# Test DB: same URL as app would use (env set above)
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{os.environ.get('POSTGRES_USER', 'postgres')}:"
    f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}"
    f"@{os.environ.get('POSTGRES_HOST', 'localhost')}:"
    f"{os.environ.get('POSTGRES_PORT', '5432')}/"
    f"{os.environ.get('POSTGRES_DB', 'pizdo_test')}"
)


@pytest.fixture(scope="function")
async def test_engine():
    """Create test engine per test to avoid event loop issues."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
def test_session_factory(test_engine):
    """Create session factory per test."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture(scope="function", autouse=True)
async def _setup_db(test_engine):
    """Clean all tables before each test (schema from Alembic in _run_migrations)."""
    async with test_engine.begin() as conn:
        tables = [t.name for t in Base.metadata.sorted_tables]
        if tables:
            await conn.execute(text("TRUNCATE " + ", ".join(tables) + " RESTART IDENTITY CASCADE"))


@pytest.fixture
def _test_get_session(test_session_factory):
    """Factory for test session."""

    async def _get() -> AsyncGenerator[AsyncSession, None]:
        """Session per request; commit so data persists across requests within a test."""
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return _get


@pytest.fixture
async def client(_test_get_session):
    """Async HTTP client. Uses test DB; data cleaned between tests."""
    app.dependency_overrides[get_session] = _test_get_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
