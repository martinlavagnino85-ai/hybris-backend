"""
city.py

This module defines the City model for the `cities` table.

Responsibilities:
- Represents cities available for property listing and guest search.
- property_count is maintained by backend logic.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    province = Column(String, nullable=False)
    property_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    # Relationships
    properties = relationship("Property", back_populates="city")
