from datetime import datetime, timezone

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import insert, select

from src.main import app
from .conftest import override_get_scoped_session
from src.core.database import User


async def test_signup_success(ac: AsyncClient):
    response = await ac.post("/auth/signup", json={"email": "test@test.ru", "password": "qwerty"})
    assert response.status_code == 200

'''

async def test_add_user(ac: AsyncClient):
    session = override_get_scoped_session()
    stmt = insert(User).values(hashed_password="test", email="test@email.ua", is_verify=True, is_admin=False, created_at=datetime.now(tz=timezone.utc))
    await session.execute(stmt)
    await session.commit()

    query = select(User)
    result = await session.execute(query)
    print("*", result.all())
    await session.close()


async def test_signup_user_already_exists():

    session = override_get_scoped_session()
    query = select(User)
    result = await session.execute(query)
    print("*", result.all())
    await session.close()
'''