from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    category: str
    price: Decimal
    stock: int
    image_url: str

    class Config:
        from_attributes = True