from fastapi import status

from src.exceptions import NotAuthenticated






class InvalidCredentials(NotAuthenticated):
    DETAIL = "Invalid credentials"
    STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY