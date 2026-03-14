"""
availability_service.py

This module contains the business logic for determining property availability.
It checks for overlapping bookings and compares them against the property's inventory_count.
"""

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.booking import Booking
from app.models.property import Property

def get_overlapping_bookings_count(db: Session, property_id: str, checkin_date: date, checkout_date: date) -> int:
    """
    Calculates the number of bookings that overlap with the requested dates for a specific property.
    
    Overlap Rule:
    requested_checkin < booking_checkout AND requested_checkout > booking_checkin
    """
    count = db.query(func.count(Booking.id)).filter(
        Booking.property_id == property_id,
        checkin_date < Booking.checkout_date,
        checkout_date > Booking.checkin_date
    ).scalar()
    
    return count or 0

def is_property_available(db: Session, property_id: str, checkin_date: date, checkout_date: date) -> bool:
    """
    Determines if a property is available for the requested dates.
    
    A property is available if the number of overlapping bookings is less than 
    its total inventory_count.
    """
    # Get the property's inventory count
    property_record = db.query(Property).filter(Property.id == property_id).first()
    
    if not property_record:
        # If the property doesn't exist, it can't be available
        return False
        
    inventory_count = property_record.inventory_count
    
    # Get the number of overlapping bookings
    overlapping_count = get_overlapping_bookings_count(db, property_id, checkin_date, checkout_date)
    
    # The property is available if we have fewer overlapping bookings than total units
    return overlapping_count < inventory_count
