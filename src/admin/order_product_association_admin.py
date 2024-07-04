from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import ProductOrderAssociation


class ProductOrderAssociationAdmin(ModelView, model=ProductOrderAssociation):
    column_list = [
        ProductOrderAssociation.id,
        ProductOrderAssociation.product_id,
        ProductOrderAssociation.product_relationship,
        ProductOrderAssociation.order_id,
        ProductOrderAssociation.order_relationship,
        ProductOrderAssociation.amount
        ]

    form_excluded_columns = []
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin'''
