import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.orders import crud, service
from src.api_v1.orders.schemas import OrderBase, UnitedOrderSchema
from src.api_v1.warehouses.dependencies import get_own_warehouse_dependency, get_warehouse_dependency
from src.core.database import User, Warehouse
from src.core.database.db_helper import db_helper
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify, get_current_user
import httpx



http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)


@router.get(path="/all")
async def get_all_orders(
        is_given_out: bool = None,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):

    orders = await service.get_all_orders(
        session=session,
        employee_id=user.id,
        is_given_out=is_given_out
    )

    return orders





@router.get(path="/united")
async def get_all_united_orders(
        warehouse: Warehouse = Depends(get_warehouse_dependency),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    orders = await service.get_united_orders(
        session=session,
        warehouse_id=warehouse.id
    )

    return orders


@router.get(path="/united/{id}")
async def get_united_order(
    order_id: str,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):
    order = await service.united_order_info(
        session=session,
        order_id=order_id,
        employee_id=user.id
    )

    return order


@router.get(path="/{order_id}")
async def get_order(
    order_id: str,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):

    order = await service.order_info(
        session=session,
        employee_id=user.id,
        order_id=order_id
    )

    return order


@router.post(
    path="/upload"
)
async def upload_united_order_view(
        file: UploadFile,
        warehouse: Warehouse = Depends(get_warehouse_dependency),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    orders_ids = await service.add_orders_from_file(session, file, user.id, warehouse.id)
    return {"The created orders": orders_ids}


@router.post(path="/give_out")
async def give_order_out(
        order_id: str,
        comment: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    order = await service.give_order_out(
        session=session,
        order_id=order_id,
        employee_id=user.id,
        comment=comment
    )

    if order:
        return order

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"order with id={order_id} not exists"
        )


@router.post(path="/notify")
async def notify_customers(
        united_order_id: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.notify_customers(
        session=session,
        united_order_id=united_order_id
    )


@router.delete(path="/delete")
async def delete_united_order(
        united_order_id: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.delete_united_order(
        session=session,
        united_order_id=united_order_id
    )
    return "Order had been deleted"














