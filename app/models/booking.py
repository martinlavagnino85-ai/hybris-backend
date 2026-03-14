"""
booking.py

This module defines the Booking model for the `bookings` table.

Responsibilities:
- Represents a finalized booking created when a guest selects one of the accepted offer candidates.
"""

from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    
    offer_id = Column(Uuid(as_uuid=True), ForeignKey("offers.id"), nullable=False)
    property_id = Column(Uuid(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    
    guest_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    host_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    checkin_date = Column(Date, nullable=False)
    checkout_date = Column(Date, nullable=False)
    nights = Column(Integer, nullable=False)
    
    price_per_night = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    # Relationships
    offer = relationship("Offer")
    property = relationship("Property")
    guest = relationship("User", foreign_keys=[guest_id])
    host = relationship("User", foreign_keys=[host_id])
