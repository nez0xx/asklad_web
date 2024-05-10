from httpx import AsyncClient
from sqlalchemy import select

from src.core.database import User
from tests.conftest import override_get_scoped_session


async def test_get_customers_list(ac: AsyncClient):

    session = override_get_scoped_session()
    stmt = select(User).where(User.email == "test@test.ru")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    user.is_verify = True
    await session.commit()
    await session.close()

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.get("/customers", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200

    response = await ac.get("/customers")
    assert response.status_code == 401

'''

@router.get(path="/{id}")
async def get_customer(
    id: str,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):

    customer = await get_customer_or_none(
        session=session,
        id=id,
        owner_id=user.id
    )

    return customer

'''

