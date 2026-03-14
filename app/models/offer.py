"""
offer.py

This module defines the Offer model for the `offers` table.
"""

from sqlalchemy import Column, Integer, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum, text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import PricingMode, OfferStatus

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    guest_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    city_id = Column(Uuid(as_uuid=True), ForeignKey("cities.id"), nullable=False)
    
    checkin_date = Column(Date, nullable=False)
    checkout_date = Column(Date, nullable=False)
    nights = Column(Integer, nullable=False)
    
    guest_count = Column(Integer, nullable=False)
    
    include_apartment = Column(Boolean, nullable=False, default=True)
    include_house = Column(Boolean, nullable=False, default=True)
    include_cabin = Column(Boolean, nullable=False, default=True)
    
    require_pets_allowed = Column(Boolean, nullable=False, default=False)
    require_children_allowed = Column(Boolean, nullable=False, default=False)
    require_pool = Column(Boolean, nullable=False, default=False)
    
    pricing_mode = Column(SQLEnum(PricingMode, name="pricing_mode_enum"), nullable=False)
    
    offered_price_per_night = Column(Integer, nullable=False)
    offered_total_amount = Column(Integer, nullable=False)
    
    duration_hours = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    status = Column(SQLEnum(OfferStatus, name="offer_status_enum"), nullable=False, default=OfferStatus.active)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    # Relationships
    guest = relationship("User", back_populates="offers_made")
    candidates = relationship("OfferCandidate", back_populates="offer")
