from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import Subscription


class SubscriptionAdmin(ModelView, model=Subscription):
    column_list = [
        Subscription.id,
        Subscription.user_id,
        Subscription.user_relationship,
        Subscription.is_active,
        Subscription.expired_at,
        Subscription.started_at,
        Subscription.created_at,
    ]
    form_excluded_columns = []
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin'''
