"""
user.py

This module defines the User model for the `users` table.

Responsibilities:
- Represents all users in the system (guests and hosts).
"""

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole, name="user_role_enum"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    # Relationships are handled dynamically or by strings to avoid circular imports.
    properties = relationship("Property", back_populates="host")
