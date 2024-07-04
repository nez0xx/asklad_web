from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.name,
        User.is_verify,
        User.is_admin,
        User.subscriptions_relationship,
        User.united_orders_relationship,
        User.warehouses_details,
    ]
    form_excluded_columns = [User.hashed_password]
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin'''
