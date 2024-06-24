from src.api_v1.exceptions import PermissionDenied


class SubscriptionNotAvailable(PermissionDenied):
    DETAIL = "Subscription not found or expired."


class LimitSubscription(PermissionDenied):
    DETAIL = "Subscriptions limit has been exceeded"
