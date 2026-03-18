
from pydantic import BaseModel
from uuid import UUID
from typing import List,Optional
from app.enums.order_status import OrderStatus
from datetime import datetime


class CreateOrderFromCartService(BaseModel):
    address_id: UUID 
    coupon_code: Optional[str] = None


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float


class OrderDetailsResponse(BaseModel):
    order_id: UUID
    order_status: str
    total_amount: float
    discount_amount: float
    final_amount: float
    coupon_code: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderSummaryResponse(BaseModel):
    order_id: UUID
    order_status: OrderStatus
    final_amount: float
    total_items: int
    created_at: datetime

    class Config:
        from_attributes = True