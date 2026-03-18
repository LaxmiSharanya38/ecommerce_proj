import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey,Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from app.database import Base


class CouponUsage(Base):
    __tablename__ = "coupon_usage"
    __table_args__ = (
    UniqueConstraint("order_id", name="uq_coupon_usage_order"),
    Index("idx_coupon_user", "coupon_id", "user_id"),
)

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    coupon_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coupons.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    used_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # relationships
    coupon = relationship("Coupon", back_populates="usages")
    user = relationship("User")
    order = relationship("Order")