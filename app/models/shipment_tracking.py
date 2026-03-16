import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum
from app.enums.shipmenttracking_status import ShipmentTrackingStatus
from app.database import Base
class ShipmentTracking(Base):
    __tablename__ = "shipment_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    shipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shipments.id")
    )

    status = Column(
    SQLEnum(
        ShipmentTrackingStatus,
        name="shipment_tracking_status_enum"
    ),
    nullable=False
)
    location = Column(String)
    updated_at = Column(DateTime, server_default=func.now())

    shipment = relationship("Shipment", back_populates="tracking_updates")