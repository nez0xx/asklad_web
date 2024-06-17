from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.warehouses.crud import get_warehouse_employee_association


async def check_user_in_employees(
        session: AsyncSession,
        employee_id: int,
        warehouse_id: int,
        auto_error=True
) -> bool:

    association = await get_warehouse_employee_association(
        session=session,
        user_id=employee_id,
        warehouse_id=warehouse_id
    )
    if (association is None) and auto_error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You not in employees list")

    return association is not None

'''
def employees_only(func):
    async def _wrapper(session: AsyncSession, employee_id: int, warehouse_id: int, *args, **kwargs):
        await check_user_in_employees(
            session=session,
            employee_id=employee_id,
            warehouse_id=warehouse_id
        )

        return await func(session=session, employee_id=employee_id, warehouse_id=warehouse_id, *args, **kwargs)

    return _wrapper
    '''

