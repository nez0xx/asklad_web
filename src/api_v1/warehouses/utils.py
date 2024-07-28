from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.warehouses.crud import get_warehouse_employee_association, get_warehouse_by_id


async def check_user_in_employees(
        session: AsyncSession,
        employee_id: int,
        warehouse_id: int,
        auto_error=True
) -> bool:

    association = await get_warehouse_employee_association(
        session=session,
        employee_id=employee_id,
        warehouse_id=warehouse_id
    )

    if (association is None) and auto_error:
        warehouse = await get_warehouse_by_id(
            session=session,
            warehouse_id=warehouse_id
        )
        if warehouse is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Warehouse with id {warehouse_id} does not exist"
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You not in employees list"
        )

    return association is not None

