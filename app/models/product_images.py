from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False
    )

    image_url = Column(String, nullable=False)

    is_primary = Column(Boolean, default=False)

    # Relationship

    product = relationship("Product", back_populates="images")