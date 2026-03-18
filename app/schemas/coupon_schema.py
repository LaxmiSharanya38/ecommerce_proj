from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional
from app.enums.discount_enum import DiscountType


class CouponCreate(BaseModel):
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    min_order_amount: Decimal = 0
    expiry_date: date
    usage_limit: int | None = None


class CouponUpdate(BaseModel):
    code: str

    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    expiry_date: Optional[date] = None
    usage_limit: Optional[int] = None
    is_active: Optional[bool] = None

class CouponResponse(BaseModel):
    id: UUID
    code: str
    discount_type: DiscountType
    discount_value: Decimal
    min_order_amount: Decimal
    expiry_date: date
    usage_limit: int | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
class ApplyCouponRequest(BaseModel):
    coupon_code: str