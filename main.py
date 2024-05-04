from api_v1.orders.products import router as products_router
from api_v1.orders import router as orders_router
from api_v1.orders.customers import router as customers_router
from api_v1.auth import router as auth_router
from fastapi import FastAPI
from fastapi import Depends
import uvicorn


app = FastAPI()
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(products_router)
app.include_router(customers_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)