from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import UnitedOrder


class UnitedOrderAdmin(ModelView, model=UnitedOrder):
    column_list = [
        UnitedOrder.id,
        UnitedOrder.warehouse_id,
        UnitedOrder.warehouse_relationship,
        UnitedOrder.delivered,
        UnitedOrder.delivery_date,
        UnitedOrder.accepted_by,
        UnitedOrder.employee_relationship,
        UnitedOrder.created_at,
        UnitedOrder.orders_relationship

    ]
    form_excluded_columns = []
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin'''
