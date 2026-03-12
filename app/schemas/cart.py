from pydantic import BaseModel
from uuid import UUID
from typing import List


class CartItemInput(BaseModel):
    product_id: UUID
    quantity: int


class AddMultipleToCartRequest(BaseModel):
    items: List[CartItemInput]



class UpdateCartItemRequest(BaseModel):
    product_id: UUID
    quantity: int