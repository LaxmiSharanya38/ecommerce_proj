from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):

    name: str
    email: EmailStr
    password: str
    phone: str


class UserResponse(BaseModel):

    id: UUID
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class UserLogin(BaseModel):

    email: EmailStr
    password: str