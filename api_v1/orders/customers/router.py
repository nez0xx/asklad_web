from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.auth.service import get_current_user
from core.database import User
from core.database.db_helper import db_helper
from .crud import get_all_customers, get_customer_or_none
from fastapi.security import HTTPBearer


http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(http_bearer)]
)


@router.get(path='/')
async def get_customers_list(
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):
    customers = await get_all_customers(
        session=session,
        owner_id=user.id
    )

    return customers


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

