from sqlalchemy import Sequence, Row

from src.api_v1.orders.customers.schemas import CustomersListItem, CustomersListSchema
from src.core.database import Customer


def validate_customers_list(customers:  Sequence[Row[tuple[Customer, int]]]):

    customers_list = []

    for item in customers:

        c = item[0]

        customer = CustomersListItem(
            name=c.name,
            id=c.atomy_id,
            orders_count=item[1]
        )

        customers_list.append(customer)

    schema = CustomersListSchema(customers=customers_list)

    return schema
