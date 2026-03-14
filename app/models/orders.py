import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


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
        String,
        default="PENDING"
    )

    total_amount = Column(Numeric(10, 2), nullable=False)

    discount_amount = Column(
        Numeric(10, 2),
        default=0
    )

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


