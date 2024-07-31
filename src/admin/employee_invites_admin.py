from sqladmin import ModelView

from src.core.database import EmployeeInvite


class EmployeeInviteAdmin(ModelView, model=EmployeeInvite):
    column_list = [
        EmployeeInvite.id,
        EmployeeInvite.token,
        EmployeeInvite.employee_id,
        EmployeeInvite.warehouse_id,
        EmployeeInvite.expire_at

    ]
