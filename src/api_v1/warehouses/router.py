from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.auth.service import get_current_user
from src.core.database import User
from src.core.database.db_helper import db_helper
from . import crud
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)


@router.get(
    path="/"
)
async def create_warehouse(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)

):
    


