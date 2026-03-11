from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Product(Base):
    __tablename__ = "products"

 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=False
    )


    sku = Column(String, unique=True, nullable=False)

    price = Column(
        Numeric(10, 2),   # total digits = 10, decimal places = 2
        nullable=False
    )

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships

    # Product → Category (Many-to-One)
    category = relationship("Category", back_populates="products")

    # Product → CartItems (One-to-Many)
    cart_items = relationship("CartItem", back_populates="product")

    # Product → Inventory (One-to-One)
    inventory = relationship(
        "Inventory",
        back_populates="product",
        uselist=False
    )

    # Product → Images (One-to-Many)
    images = relationship("ProductImage", back_populates="product")