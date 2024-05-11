from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.auth.service import get_current_user
from src.core.database import User
from src.core.database.db_helper import db_helper
from .crud import get_all_customers, get_customer_or_none
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify
from .schemas import CustomersListSchema
from .validators import validate_customers_list

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)


@router.get(
    path='/',
    response_model=CustomersListSchema
)
async def get_customers_list(
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):
    customers = await get_all_customers(
        session=session,
        owner_id=user.id
    )

    schema = validate_customers_list(customers)

    return schema


@router.get(path="/{customer_id}")
async def get_customer(
    customer_id: str,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):

    customer = await get_customer_or_none(
        session=session,
        customer_atomy_id=customer_id,
        owner_id=user.id
    )

    if customer:
        return customer

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with {customer_id} does not exist")

