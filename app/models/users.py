from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String)

    email = Column(String, unique=True)

    password_hash = Column(String)

    phone = Column(String)

    is_active = Column(Boolean, default=True)