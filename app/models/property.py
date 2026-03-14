"""
property.py

This module defines the Property model for the `properties` table.

Responsibilities:
- Represents properties listed by hosts.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum, text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import PropertyType

class Property(Base):
    __tablename__ = "properties"

    id = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    host_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    city_id = Column(Uuid(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    property_type = Column(SQLEnum(PropertyType, name="property_type_enum"), nullable=False)
    
    max_guests = Column(Integer, nullable=True)
    room_count = Column(Integer, nullable=True)
    
    inventory_count = Column(Integer, nullable=False, default=1)
    
    pets_allowed = Column(Boolean, nullable=True)
    children_allowed = Column(Boolean, nullable=True)
    pool_available = Column(Boolean, nullable=True)
    
    price_reference = Column(Integer, nullable=True)
    base_min_nights = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    # Relationships
    host = relationship("User", back_populates="properties")
    city = relationship("City", back_populates="properties")
    filters = relationship("PropertyOfferFilter", back_populates="property")
