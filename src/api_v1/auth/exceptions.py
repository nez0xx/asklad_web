from src.exceptions import NotAuthenticated

from fastapi import status


class InvalidCredentials(NotAuthenticated):
    DETAIL = "Invalid email or password"
    STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY


class InvalidToken(NotAuthenticated):
    DETAIL = "Invalid token"
