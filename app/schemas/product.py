from pydantic import BaseModel, Field
from uuid import UUID  
from decimal import Decimal
from typing import List,Optional


class ProductCreate(BaseModel):
    name: str
    description: str
    category_id: UUID
    price: Decimal
    quantity_available: int = Field(..., ge=0)
    sku:str
    images: List[str]


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    is_active: bool

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    price: Optional[Decimal] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None
    quantity_available: Optional[int] = None
    images: Optional[List[str]] = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    price: Decimal
    is_active: bool

    class Config:
        from_attributes = True