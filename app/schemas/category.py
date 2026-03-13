from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]

    class Config:
        from_attributes = True
