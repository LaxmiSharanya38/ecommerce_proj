import uuid
from datetime import datetime

from sqlalchemy import  Column,String,Boolean,Date,DateTime,Integer,Numeric,Enum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums.discount_enum import DiscountType


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    code = Column(String, unique=True, nullable=False, index=True)

    discount_type = Column(
        Enum(DiscountType, name="discount_type_enum"),
        nullable=False
    )

    discount_value = Column(
        Numeric(10, 2),
        nullable=False
    )

    min_order_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    expiry_date = Column(Date, nullable=False)

    usage_limit = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # relationships
    usages = relationship(
        "CouponUsage",
        back_populates="coupon",
        cascade="all, delete-orphan"
    )