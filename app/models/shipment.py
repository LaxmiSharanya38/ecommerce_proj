import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum
from app.enums.shipment_status import ShipmentStatus
from app.database import Base
class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        unique=True
    )

    courier_name = Column(String)  
    tracking_number = Column(String)

    shipment_status = Column(
    SQLEnum(ShipmentStatus, name="shipment_status_enum"),
    nullable=False,
    default=ShipmentStatus.CREATED
)

    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="shipment")
    tracking_updates = relationship(
        "ShipmentTracking",
        back_populates="shipment",
         cascade="all, delete-orphan",
    order_by="ShipmentTracking.updated_at"
    )