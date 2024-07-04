from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import WarehouseEmployeeAssociation


class WarehouseEmployeeAssociationAdmin(ModelView, model=WarehouseEmployeeAssociation):
    column_list = [
        WarehouseEmployeeAssociation.id,
        WarehouseEmployeeAssociation.warehouse_id,
        WarehouseEmployeeAssociation.warehouse_relationship,
        WarehouseEmployeeAssociation.user_id,
        WarehouseEmployeeAssociation.employee_relationship
        ]

    form_excluded_columns = []
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin'''
