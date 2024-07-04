from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import Warehouse


class WarehouseAdmin(ModelView, model=Warehouse):
    column_list = [
        Warehouse.id,
        Warehouse.owner_id,
        Warehouse.name,
        Warehouse.employees_details,
        Warehouse.created_at,
        Warehouse.orders_relationship,
        ]

    form_excluded_columns = []
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin'''
