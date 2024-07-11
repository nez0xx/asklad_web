from sqladmin import ModelView
from starlette.requests import Request

from src.core.database import Tariff


class TariffAdmin(ModelView, model=Tariff):
    column_list = [
        Tariff.id,
        Tariff.tariff_name,
        Tariff.price_rub,
        Tariff.price_byn,
        Tariff.price_kzt,
        Tariff.expire_days,
        Tariff.subscriptions_relationship
    ]

