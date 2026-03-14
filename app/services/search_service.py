"""
search_service.py

This module contains the logic for finding available properties based on user searches.
It orchestrates structural filtering, availability verification, and economic threshold calculations.
"""

from datetime import date
from sqlalchemy.orm import Session
from app.models import Property
from app.services.economic_service import calculate_nights, calculate_effective_threshold
from app.services.availability_service import is_property_available

def search_available_properties(
    db: Session, 
    city_id: str, 
    checkin_date: date, 
    checkout_date: date, 
    guest_count: int
) -> list[dict]:
    """
    Orchestrates the property search, returning properties that meet all criteria:
    1. Structural features (city, max_guests, base_min_nights, is_active).
    2. Availability (no overlapping bookings over inventory capacity).
    3. Economic viability (must have a valid price threshold for the requested length of stay).
    
    Returns a list of dicts containing the Property instance and its effective_threshold.
    """
    nights = calculate_nights(checkin_date, checkout_date)
    if nights <= 0:
        return []
        
    # Step 1: Structural Filtering
    properties = db.query(Property).filter(
        Property.city_id == city_id,
        Property.is_active == True,
        Property.max_guests >= guest_count,
        Property.base_min_nights <= nights
    ).all()
    
    results = []
    
    for prop in properties:
        # Step 2: Availability Verification
        if not is_property_available(db, prop.id, checkin_date, checkout_date):
            continue
            
        # Step 3: Economic Threshold Calculation
        threshold = calculate_effective_threshold(db, prop.id, nights)
        
        # If no valid filter exists for this length of stay, the property is not offered
        if threshold is not None:
            # Step 4: Result Assembly
            results.append({
                "property": prop,
                "effective_threshold": threshold
            })
            
    return results
