from enum import Enum

class OrderStatus(str, Enum):
    CREATED = "created"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
class RefundStatus(str, Enum):
    NONE = "none"           # default
    PENDING = "pending"     # refund in progress
    COMPLETED = "completed"
    FAILED = "failed"