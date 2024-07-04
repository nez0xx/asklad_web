from sqladmin import Admin

from src.admin import full_admin_views_list
from src.api_v1.orders.products import router as products_router
from src.api_v1.orders import router as orders_router
# from src.api_v1.orders.customers import router as customers_router
from src.api_v1.subscriptions import router as subscriptions_router
from src.api_v1.auth import router as auth_router
from src.api_v1.warehouses import router as warehouses_router, invite_router
from fastapi import FastAPI
import uvicorn

from src.core.database import db_helper

app = FastAPI()

admin = Admin(
    app=app,
    engine=db_helper.engine
)

for admin_view in full_admin_views_list:
    admin.add_view(admin_view)

app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(products_router)
# app.include_router(customers_router)
app.include_router(warehouses_router)
app.include_router(invite_router)
app.include_router(subscriptions_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
