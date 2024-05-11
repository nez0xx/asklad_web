from httpx import AsyncClient
from sqlalchemy import select

from src.core.database import User, Customer
from tests.conftest import override_get_scoped_session


async def test_get_customers_list(ac: AsyncClient):

    # активация юзера вручную, чтоб можно было пройти проверку зависимости check_user_is_verify
    session = override_get_scoped_session()
    stmt = select(User).where(User.email == "test@test.ru")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    user.is_verify = True
    await session.commit()
    await session.close()

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    customer1 = Customer(name="Mihail", atomy_id="id1", owner=user.atomy_id)
    customer2 = Customer(name="Sergey", atomy_id="id2", owner=user.atomy_id)

    session = override_get_scoped_session()
    session.add(customer1)
    session.add(customer2)
    await session.commit()
    await session.close()

    response = await ac.get("/customers/", headers={"Authorization": f"Bearer {access_token}"})
    # orders_count = 1, потому что минимум одна запись из левой при джоине будет найдена и посчитана за заказ
    assert response.json() == {"customers": [
        {"name": "Mihail", "id": "id1", "orders_count": 1},
        {"name": "Sergey", "id": "id2", "orders_count": 1}
    ]}

    response = await ac.get("/customers/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


async def test_get_customer(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]
    
    response = await ac.get("/customers/id1", headers={"Authorization": f"Bearer {access_token}"})
    assert response.json() == {"id": "id1", "name": "Mihail", "owner": 1, "orders": []}

    response = await ac.get("/customers/id1")
    assert response.status_code == 403

    response = await ac.get("customers/RANDOM_ID", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Customer with RANDOM_ID does not exist"}



