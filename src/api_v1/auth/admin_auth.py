from sqladmin.authentication import AuthenticationBackend

from fastapi import Request

from src.api_v1.auth.crud import get_user_by_email
from src.api_v1.auth.exceptions import InvalidCredentials, InvalidToken
from src.api_v1.auth.security import check_password
from src.api_v1.auth.utils import create_access_token
from src.api_v1.utils import decode_jwt
from src.core import settings
from src.core.database import db_helper
from src.exceptions import PermissionDenied


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        async_session = db_helper.get_scoped_session()

        user_model = await get_user_by_email(session=async_session, email=username)

        if user_model is None:
            raise InvalidCredentials()

        await async_session.close()

        if not check_password(
            password=password,
            hashed_password=user_model.hashed_password,
        ):
            raise InvalidCredentials()

        if not user_model.is_admin:
            raise PermissionDenied()

        access_token = create_access_token(user_email=user_model.email)

        request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False
        try:
            decode_jwt(token=token)
        except Exception as e:
            raise InvalidToken()

        return True


authentication_backend = AdminAuth(secret_key=settings.auth_jwt.private_key_path.read_text())
