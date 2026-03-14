"""
offer_candidate.py

This module defines the OfferCandidate model for the `offer_candidates` table.

Responsibilities:
- Represents the relationship between an offer and each property that received it.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SQLEnum, text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.enums import HostResponse

class OfferCandidate(Base):
    __tablename__ = "offer_candidates"

    id = Column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    
    offer_id = Column(Uuid(as_uuid=True), ForeignKey("offers.id"), nullable=False)
    property_id = Column(Uuid(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    
    effective_threshold = Column(Integer, nullable=False)
    
    host_response = Column(SQLEnum(HostResponse, name="host_response_enum"), nullable=False, default=HostResponse.pending)
    
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))

    # Relationships
    offer = relationship("Offer", back_populates="candidates")
    property = relationship("Property")
