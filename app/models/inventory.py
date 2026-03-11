from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        unique=True,          # one inventory per product
        nullable=False
    )

    quantity_available = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship

    product = relationship("Product", back_populates="inventory")