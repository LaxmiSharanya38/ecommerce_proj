import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        unique=True
    )
    # one invoice per order

    invoice_number = Column(String, unique=True, nullable=False)

    invoice_url = Column(String, nullable=False)
    # stored PDF location (S3/local)

    generated_at = Column(
        DateTime,
        server_default=func.now()
    )

    # relationship
    order = relationship("Order", back_populates="invoice")