from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.auth.dependencies import get_current_user
from src.api_v1.subscriptions import crud
from src.core.database import User, db_helper, Subscription


async def check_active_subscription_depends(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
) -> Subscription | None:
    subscription_model = await crud.get_active_subscription_by_user_id(
        user_id=user.id,
        session=session
    )

    if not subscription_model:
        raise SubscriptionNotAvailable()

    return subscription_model