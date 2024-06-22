class SubscriptionNotAvailable(PermissionDenied):
    DETAIL = "Subscription not found or expired."


class LimitSubscription(PermissionDenied):
    DETAIL = "Subscriptions limit has been exceeded"
