import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum
from app.database import Base
from app.enums.order_status import OrderStatus,RefundStatus

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    address_id = Column(
        UUID(as_uuid=True),
        ForeignKey("addresses.id"),
        nullable=False
    )

    order_status = Column(
    SQLEnum(OrderStatus, name="order_status_enum"),
    nullable=False,
    default=OrderStatus.CREATED)
    
    total_amount = Column(Numeric(10, 2), nullable=False)

    discount_amount = Column(
        Numeric(10, 2),
        default=0
    )
    coupon_id = Column(
    UUID(as_uuid=True),
    ForeignKey("coupons.id"),
    nullable=True
)

    coupon_code = Column(String, nullable=True)
    final_amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now()
    )
    cancelled_at = Column(DateTime, nullable=True)
    refund_status = Column(
        SQLEnum(RefundStatus, name="refund_status_enum"),
        nullable=False,
        default=RefundStatus.NONE
    )

    # relationships
    user = relationship("User", back_populates="orders")
    address = relationship("Address")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete"
    )

    payments = relationship(
    "Payment",
    back_populates="order",
    cascade="all, delete"
)

    shipment = relationship(
        "Shipment",
        back_populates="order",
        uselist=False
    )

    invoice = relationship(
        "Invoice",
        back_populates="order",
        uselist=False
    )

    coupon = relationship("Coupon", back_populates="orders")
    coupon_usage = relationship(
    "CouponUsage",
    back_populates="order",
    uselist=False
)