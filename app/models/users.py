from sqlalchemy import Column, String, Boolean,DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String)

    email = Column(String, unique=True)

    password_hash = Column(String)

    phone = Column(String)

    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)
    addresses = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete"
    )
    # Relationship
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")