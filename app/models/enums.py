"""
enums.py

This module defines all the enumerations used across the database models.
These map to PostgreSQL ENUM types.
"""

import enum

class UserRole(str, enum.Enum):
    guest = "guest"
    host = "host"

class PropertyType(str, enum.Enum):
    apartment = "apartment"
    house = "house"
    cabin = "cabin"

class PricingMode(str, enum.Enum):
    nightly_rate = "nightly_rate"
    total_budget = "total_budget"

class OfferStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    completed = "completed"

class HostResponse(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
