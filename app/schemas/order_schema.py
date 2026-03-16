
from pydantic import BaseModel
from uuid import UUID
from typing import List
from app.enums.order_status import OrderStatus
from datetime import datetime


class CreateOrderFromCartService(BaseModel):
    address_id: UUID


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float

class OrderDetailsResponse(BaseModel):
    order_id: int
    status: str
    total_amount: float
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