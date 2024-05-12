from httpx import AsyncClient
from sqlalchemy import select

from src.core.database import Product
from tests.conftest import override_get_scoped_session


async def test_get_all_products_view(ac: AsyncClient):

    response = await ac.get("/products/")
    assert response.status_code == 403

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.get("/products/", headers={"Authorization": f"Bearer {access_token}"})
    print(response.json())
    assert response.json() == [
        {
            'amount': 0,
            'owner': 1,
            'title': 'Toothpaste',
            'atomy_id': 'product1',
            'id': 1
        },
        {
            'amount': 2599,
            'owner': 1,
            'title': 'Vitamin C',
            'atomy_id': 'product2',
            'id': 2
        }
    ]


async def test_get_product(ac: AsyncClient):
    
    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.get("/products/RANDOM_ID", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404

    response = await ac.get("/products/product2", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {
        'amount': 2599,
        'owner': 1,
        'title': 'Vitamin C',
        'atomy_id': 'product2',
        'id': 2,
        'orders_details': [
            {
                'order_id': 'order2',
                'amount': 2599,
                'id': 2,
                'product_id': 2
            }
        ]
    }


async def test_update_product_view(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.patch("/products/product1", json={"title": "NEW TITLE"}, headers={"Authorization": f"Bearer {access_token}"})

    session = override_get_scoped_session()
    stmt = select(Product).where(Product.id == 1)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    assert product.title == "NEW TITLE"
    await session.close()

    assert response.status_code == 200

