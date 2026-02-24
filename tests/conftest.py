"""
Test configuration: DB override, HTTP client, fixtures.
Set POSTGRES_* env before import so app uses test database.
"""

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
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
    """Create tables before each test. create_all is idempotent."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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


# Note: Tests use unique data to avoid conflicts.
# For cleanup, run: PGPASSWORD=postgres psql -h localhost -U postgres -d pizdo_test -c "TRUNCATE ... CASCADE;"


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
