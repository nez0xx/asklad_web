from datetime import datetime, timezone

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import insert, select

from src.main import app
from .conftest import override_get_scoped_session


async def test_register_user(ac: AsyncClient):

    response = await ac.post("/auth/signup", json={"email": "test@test.ru", "password": "qwerty"})
    assert response.status_code == 200

    response = await ac.post("/auth/signup", json={"email": "RANDOM_STRING", "password": "qwerty"})
    assert response.status_code == 422

    response = await ac.post("/auth/signup", json={"email": "test@test.ru", "password": "qwerty"})
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


async def test_auth_user_issue_jwt(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    assert response.status_code == 200

    response = await ac.post("/auth/login", json={"email": "error@test.ru", "password": "error"})
    assert response.status_code == 401


async def test_refresh_token(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    refresh_token = response.json().get("refresh_token")

    response = await ac.get("/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    access_token = response.json().get("access_token")

    response = await ac.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    response = await ac.get("/auth/refresh", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid token type: refresh expected"}

    response = await ac.get("/auth/refresh", headers={"Authorization": f"Bearer RANDOM_STRING"})
    assert response.status_code == 401

'''

@router.get("/confirm/{token}")
async def test_confirm_email_view(
    token: str,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    ac: AsyncClient
):
    await service.confirm_email(session, token)
'''