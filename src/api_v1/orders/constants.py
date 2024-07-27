class ErrorCode:
    """
    Константы для описания ошибок в модуле заказов.
    """
    ORDER_NOT_FOUND = "Заказ не найден"
    ORDER_IS_GIVEN_OUT = "Заказ уже выдан"
    ORDER_ALREADY_EXISTS = "Заказ уже существует"

    UNITED_ORDER_NOT_FOUND = "Консолидированный заказ не найден"
    UNITED_ORDER_NOT_DELIVERED = "Консолидированный заказ не доставлен"
    UNITED_ORDER_ALREADY_EXISTS = "Консолидированный заказ уже существует"
    UNITED_ORDER_ALREADY_DELIVERED = "Консолидированный заказ уже доставлен"

    WAREHOUSE_NOT_FOUND = "Вы не управляете складом"
