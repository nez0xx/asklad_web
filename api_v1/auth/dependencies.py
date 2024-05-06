from fastapi import Depends, HTTPException, status
from .service import get_current_user
from core.database import User


def check_user_is_verify(user: User = Depends(get_current_user)):
    if not user.is_verify:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verify your account")
