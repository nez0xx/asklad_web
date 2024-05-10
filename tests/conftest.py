import asyncio
from asyncio import current_task
from typing import AsyncGenerator

from httpx import AsyncClient
import pytest

from src.core.database import db_helper, Base
from src.core.settings import settings
from src.main import app

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)

engine = create_async_engine(url=settings.test_db_url)

session_factory = async_sessionmaker(
                bind=engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
)


def override_get_scoped_session():
    session = async_scoped_session(
        session_factory=session_factory,
        scopefunc=current_task
    )
    return session


async def override_get_scoped_session_dependency():
    session = override_get_scoped_session()
    yield session
    await session.close()

app.dependency_overrides[db_helper.get_scoped_session_dependency] = override_get_scoped_session_dependency


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac



