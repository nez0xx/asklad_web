from httpx import AsyncClient
from sqlalchemy import select

from src.core.database import Order
from tests.conftest import override_get_scoped_session

order = {
        "id": "order1",
        "customer_phone": "88005553535",
        "customer": {
            "name": "Mihail",
            "atomy_id": "id1"
        },
        "products": [
            {
                "title": "Toothpaste",
                "amount": 5,
                "atomy_id": "product1"
            }
        ]
    }

order2 = {
        "id": "order2",
        "customer_phone": "88005553535",
        "customer": {
            "name": "Mihail",
            "atomy_id": "id1"
        },
        "products": [
            {
                "title": "Vitamin C",
                "amount": 2599,
                "atomy_id": "product2"
            }
        ]
    }


async def test_create_order_view(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.post("/orders/", json=order)
    assert response.status_code == 403

    response = await ac.post("/orders/", json=order, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"The created order id": order["id"]}

    response = await ac.post("/orders/", json=order2, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    response = await ac.post("/orders/", json=order, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 409
    assert response.json() == {"detail": f"Order with id {order["id"]} already exists"}

    response = await ac.post("/orders/", json={"id": 123}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422






async def test_get_orders(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.get("/orders/")
    assert response.status_code == 403

    response = await ac.get("/orders/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    print(response.json())
    assert response.json() == [
        {
            'id': 'order1',
            'owner': 1,
            'is_given_out': False,
            'customer_phone': '88005553535',
            'customer_id': 1,
            'customer_relationship':
                {
                    'atomy_id': 'id1',
                    'id': 1, 'name':
                    'Mihail',
                    'owner': 1
                },
            'products_details': [
                {
                    'order_id': 'order1',
                    'amount': 5,
                    'id': 1,
                    'product_id': 1
                }
                ]
            },
        {
            'id': 'order2',
            'owner': 1,
            'is_given_out': False,
            'customer_phone': '88005553535',
            'customer_id': 1,
            'customer_relationship':
                {
                    'atomy_id': 'id1',
                    'id': 1, 'name':
                    'Mihail',
                    'owner': 1
                },
            'products_details': [
                {
                    'order_id': 'order2',
                    'amount': 2599,
                    'id': 2,
                    'product_id': 2
                }]
            }
        ]


async def test_give_order_out(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.post(
        f"/orders/give_out",
        params={"order_id": "order1"},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200

    session = override_get_scoped_session()
    stmt = select(Order).where(Order.id == "order1")
    result = await session.execute(stmt)
    order_1 = result.scalar_one_or_none()
    assert order_1.is_given_out is True
    await session.close()




