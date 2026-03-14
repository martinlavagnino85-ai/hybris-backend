"""
economic_service.py

This module contains the business logic for calculating dates, nights, and prices.
It calculates the effective_threshold for properties based on their filters.
"""

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.property_offer_filter import PropertyOfferFilter
from app.models.enums import PricingMode

def calculate_nights(checkin_date: date, checkout_date: date) -> int:
    """
    Calculates the total number of nights between two dates.
    Returns 0 if checkin >= checkout.
    """
    if checkin_date >= checkout_date:
        return 0
    return (checkout_date - checkin_date).days

def calculate_effective_threshold(db: Session, property_id: str, requested_nights: int) -> int | None:
    """
    Calculates the minimum acceptable price per night for a given property
    based on the requested length of stay.
    
    Formula: MIN(price_per_night) where min_nights <= requested_nights
    """
    threshold = db.query(func.min(PropertyOfferFilter.price_per_night)).filter(
        PropertyOfferFilter.property_id == property_id,
        PropertyOfferFilter.min_nights <= requested_nights
    ).scalar()
    
    return threshold

def convert_rate(amount: int, nights: int, from_mode: PricingMode, to_mode: PricingMode) -> int:
    """
    Converts pricing structures between total_budget and nightly_rate.
    """
    if from_mode == to_mode:
        return amount
        
    if nights <= 0:
        return 0
        
    if from_mode == PricingMode.nightly_rate and to_mode == PricingMode.total_budget:
        return amount * nights
        
    if from_mode == PricingMode.total_budget and to_mode == PricingMode.nightly_rate:
        # We use integer division to ensure amounts remain cleanly formatted 
        # (Though in production, monetary rounding might be required)
        return amount // nights
        
    return amount
