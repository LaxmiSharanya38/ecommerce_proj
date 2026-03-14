import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
class ShipmentTracking(Base):
    __tablename__ = "shipment_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    shipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shipments.id")
    )

    status = Column(String)
    location = Column(String)
    updated_at = Column(DateTime, server_default=func.now())

    shipment = relationship("Shipment", back_populates="tracking_updates")