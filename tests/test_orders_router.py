from httpx import AsyncClient


order = {
        "id": "order1",
        "customer_phone": "88005553535",
        "customer": {
            "name": "Mihail",
            "id": "id1"
        },
        "products": [
            {
                "title": "Toothpaste",
                "amount": 5,
                "id": "product1"
            }
        ]
    }


async def test_create_order_view(ac: AsyncClient):

    response = await ac.post("/auth/login", json={"email": "test@test.ru", "password": "qwerty"})
    access_token = response.json()["access_token"]

    response = await ac.post("/orders/create_order", json=order)
    assert response.status_code == 403

    response = await ac.post("/orders/create_order", json=order, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"The created order id": order["id"]}

    response = await ac.post("/orders/create_order", json=order, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 409
    assert response.json() == {"detail": f"Order with id {order["id"]} already exists"}

    response = await ac.post("/orders/create_order", json={"id": 123}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422






async def test_get_orders(ac: AsyncClient):

    response = ac.get("/orders/")



async def test_give_order_out(ac: AsyncClient):
    response = ac.post("/orders/give_out")


async def test_get_order(ac: AsyncClient
):
    response = ac.post("/orders/order1")



