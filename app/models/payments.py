import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False
    )

    provider = Column(String, nullable=False)  
    # example: stripe, razorpay, paypal

    payment_status = Column(String, default="PENDING")
    # PENDING / SUCCESS / FAILED / REFUNDED

    transaction_id = Column(String, nullable=True)

    amount = Column(Numeric(10,2), nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        onupdate=func.now()
    )

    # relationship
    order = relationship("Order", back_populates="payments")