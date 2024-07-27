from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import Product


class ProductAdmin(ModelView, model=Product):
    column_list = [
        Product.id,
        Product.title,
        Product.price,
        Product.pv,
        Product.orders_details

    ]
    form_excluded_columns = []
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin'''
