from sqladmin import ModelView

from src.core.database import ResetToken


class ResetTokenAdmin(ModelView, model=ResetToken):
    column_list = [
        ResetToken.id,
        ResetToken.token,
        ResetToken.user_id,
        ResetToken.expired_at
    ]
    form_excluded_columns = []
