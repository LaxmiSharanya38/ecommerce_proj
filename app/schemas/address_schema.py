from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class AddressCreate(BaseModel):
    address_line1: str
    city: str
    state: str
    country: str
    pincode: str
    


class AddressResponse(AddressCreate):
    id: UUID

    class Config:
        from_attributes = True

class AddressUpdate(BaseModel):
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
