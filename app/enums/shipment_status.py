from enum import Enum
class ShipmentStatus(str, Enum):
    CREATED = "created"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"