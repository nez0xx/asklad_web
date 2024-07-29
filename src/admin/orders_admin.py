from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import Order


class OrderAdmin(ModelView, model=Order):
    column_list = [
        Order.id,
        Order.united_order_id,
        Order.united_order_relationship,
        Order.customer_phone,
        Order.customer_id,
        Order.customer_name,
        Order.customer_relationship,
        Order.created_at,
        Order.comment,
        Order.warehouse_id,
        Order.given_by,
        Order.is_given_out,
        Order.issue_date,
        Order.products_details

    ]
    form_excluded_columns = []
    '''
    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user.is_admin
        '''
