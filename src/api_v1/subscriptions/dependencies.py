from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.auth.dependencies import get_current_user
from src.api_v1.subscriptions import crud
from src.api_v1.subscriptions.exceptions import SubscriptionNotAvailable
from src.api_v1.warehouses.dependencies import get_warehouse_dependency
from src.core.database import User, db_helper, Subscription, Warehouse


async def check_active_subscription_depends(
        user: User = Depends(get_current_user),
        warehouse: Warehouse = Depends(get_warehouse_dependency),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
) -> Subscription | None:

    owner_id = warehouse.owner_id
    subscription_model = await crud.get_active_subscription_by_user_id(
        user_id=owner_id,
        session=session
    )
    if subscription_model is None:
        raise SubscriptionNotAvailable()

    return subscription_model