"""
property_offer_filter.py

This module defines the PropertyOfferFilter model for the `property_offer_filters` table.

Responsibilities:
- Defines the pricing filters for each property.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, text, UniqueConstraint
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base

class PropertyOfferFilter(Base):
    __tablename__ = "property_offer_filters"

    id = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    property_id = Column(Uuid(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    
    min_nights = Column(Integer, nullable=False)
    price_per_night = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    # Constraints: 
    # Each property must not have duplicate min_nights or duplicate price_per_night values.
    __table_args__ = (
        UniqueConstraint('property_id', 'min_nights', name='uq_property_min_nights'),
        UniqueConstraint('property_id', 'price_per_night', name='uq_property_price_per_night'),
    )

    # Relationships
    property = relationship("Property", back_populates="filters")
