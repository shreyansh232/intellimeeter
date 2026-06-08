import asyncio
from typing import AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.database.db import Base, get_db
from app.main import app

settings = get_settings()

# Use a test database
TEST_DATABASE_URL = settings.database_url + "_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def create_test_db():
    # Connect to default postgres database to create the test database
    admin_url = settings.database_url.replace("intellimeeter", "postgres")
    # Use asyncpg directly for DB creation as SQLAlchemy doesn't support it well
    conn_str = admin_url.replace("postgresql+asyncpg://", "")
    user_pass, host_port_db = conn_str.split("@")
    user, password = user_pass.split(":")
    host_port, _ = host_port_db.split("/")

    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host_port.split(":")[0],
        port=host_port.split(":")[1] if ":" in host_port else 5432,
        database="postgres",
    )
    try:
        await conn.execute("CREATE DATABASE intellimeeter_test")
    except asyncpg.exceptions.DuplicateDatabaseError:
        pass
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    try:
        await create_test_db()
    except Exception as e:
        print(f"Warning: Could not create test database: {e}")

    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL)
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with TestingSessionLocal() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
