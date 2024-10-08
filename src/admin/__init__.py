__all__ = (
    "full_admin_views_list",
)

from .users_admin import UserAdmin
from .orders_admin import OrderAdmin
from .warehouses_admin import WarehouseAdmin
from .products_admin import ProductAdmin
from .subscriptions_admin import SubscriptionAdmin
from .united_orders_admin import UnitedOrderAdmin
from .warehouse_employee_association_admin import WarehouseEmployeeAssociationAdmin
from .order_product_association_admin import ProductOrderAssociationAdmin
from .tariffs_admin import TariffAdmin
from .reset_tokens_admin import ResetTokenAdmin
from .email_tokens_admin import EmailConfirmTokenAdmin
from .payments_admin import PaymentAdmin
from .employee_invites_admin import EmployeeInviteAdmin

full_admin_views_list = [
    UserAdmin,
    OrderAdmin,
    WarehouseAdmin,
    ProductAdmin,
    SubscriptionAdmin,
    UnitedOrderAdmin,
    WarehouseEmployeeAssociationAdmin,
    ProductOrderAssociationAdmin,
    TariffAdmin,
    ResetTokenAdmin,
    EmailConfirmTokenAdmin,
    EmployeeInviteAdmin,
    PaymentAdmin
]
