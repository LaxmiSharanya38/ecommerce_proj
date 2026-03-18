from pydantic import BaseModel
from uuid import UUID
from typing import List,Optional


class CartItemInput(BaseModel):
    product_id: UUID
    quantity: int


class AddMultipleToCartRequest(BaseModel):
    items: List[CartItemInput]



class UpdateCartItemRequest(BaseModel):
    product_id: UUID
    quantity: int
class CartResponse(BaseModel):
    id: str
    total_amount: float

    coupon_code: Optional[str] = None
    discount_amount: float
    final_amount: float

    class Config:
        from_attributes = True