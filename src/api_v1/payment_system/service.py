import uuid

from yookassa import Configuration, Payment

Configuration.account_id = 435233
Configuration.secret_key = "test_m89h64uRzryHS4pc754-SMAdUzngt3i8a3vRc3faHKE"

payment = Payment.create({
    "amount": {
        "value": "100.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://asklad.pro"
    },
    "capture": True,
    "description": "Заказ №37"
}, uuid.uuid4())

print(payment["confirmation"]["confirmation_url"])