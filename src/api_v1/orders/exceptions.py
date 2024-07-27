from src.api_v1.orders.constants import ErrorCode
from src.exceptions import DetailedHTTPException, NotFound, Conflict


class NotDelivered(Conflict):
    DETAIL = ErrorCode.UNITED_ORDER_NOT_DELIVERED


class AlreadyDelivered(Conflict):
    DETAIL = ErrorCode.UNITED_ORDER_ALREADY_DELIVERED


class UnitedOrderExists(Conflict):
    DETAIL = ErrorCode.UNITED_ORDER_ALREADY_EXISTS


class UnitedOrderNotFound(NotFound):
    DETAIL = ErrorCode.UNITED_ORDER_NOT_FOUND


class OrderExists(Conflict):
    DETAIL = ErrorCode.ORDER_ALREADY_EXISTS


class OrderNotFound(NotFound):
    DETAIL = ErrorCode.ORDER_NOT_FOUND


class WarehouseNotFound(NotFound):
    DETAIL = ErrorCode.WAREHOUSE_NOT_FOUND


class OrderIsGivenOut(Conflict):
    DETAIL = ErrorCode.ORDER_IS_GIVEN_OUT
