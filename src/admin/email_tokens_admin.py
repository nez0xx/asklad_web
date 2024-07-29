from sqladmin import ModelView

from src.core.database import EmailConfirmToken


class EmailConfirmTokenAdmin(ModelView, model=EmailConfirmToken):
    column_list = [
        EmailConfirmToken.id,
        EmailConfirmToken.token,
        EmailConfirmToken.user_id,
        EmailConfirmToken.user_relationship,
        EmailConfirmToken.created_at
        ]

    form_excluded_columns = []
