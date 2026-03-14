"""
test_availability.py

Script to test the availability service logic against a local SQLite database or Postgres.
"""

import sys
import os
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, engine
from app.models import User, City, Property, Booking
from app.models.enums import UserRole, PropertyType, PricingMode, OfferStatus
from app.models import User, City, Property, Booking, Offer
from app.services.availability_service import is_property_available, get_overlapping_bookings_count
from datetime import date, timedelta, datetime, timezone

def setup_test_data(db):
    print("Setting up test data...")
    # Create test user (host)
    host = User(
        name="Test Host",
        email="test_host_avail@example.com",
        password_hash="fakehash",
        role=UserRole.host
    )
    db.add(host)
    db.flush()

    # Create test user (guest)
    guest = User(
        name="Test Guest",
        email="test_guest_avail@example.com",
        password_hash="fakehash",
        role=UserRole.guest
    )
    db.add(guest)
    db.flush()

    # Create dummy city
    city = City(
        name="Availability City",
        province="Test Province",
        property_count=2
    )
    db.add(city)
    db.flush()

    # Create property with inventory = 1
    prop1 = Property(
        host_id=host.id,
        city_id=city.id,
        title="Single Unit Property",
        property_type=PropertyType.apartment,
        inventory_count=1,
        max_guests=2,
        room_count=1,
        pets_allowed=False,
        children_allowed=True,
        pool_available=False,
        price_reference=25000,
        base_min_nights=1
    )
    db.add(prop1)
    
    # Create property with inventory = 2
    prop2 = Property(
        host_id=host.id,
        city_id=city.id,
        title="Double Unit Property",
        property_type=PropertyType.apartment,
        inventory_count=2,
        max_guests=4,
        room_count=2,
        pets_allowed=True,
        children_allowed=True,
        pool_available=True,
        price_reference=50000,
        base_min_nights=2
    )
    db.add(prop2)
    db.flush()
    
    # Create a dummy offer to satisfy booking foreign key
    offer = Offer(
        guest_id=guest.id,
        city_id=city.id,
        checkin_date=date(2026, 4, 1),
        checkout_date=date(2026, 4, 30),
        nights=30,
        guest_count=2,
        pricing_mode=PricingMode.nightly_rate,
        offered_price_per_night=25000,
        offered_total_amount=750000,
        duration_hours=24,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        status=OfferStatus.active
    )
    db.add(offer)
    db.flush()

    return host, guest, prop1, prop2, offer

def create_booking(db, prop_id, offer_id, guest_id, host_id, checkin, checkout):
    booking = Booking(
        offer_id=offer_id, 
        property_id=prop_id,
        guest_id=guest_id,
        host_id=host_id,
        checkin_date=checkin,
        checkout_date=checkout,
        nights=(checkout - checkin).days,
        price_per_night=25000,
        total_amount=25000 * (checkout - checkin).days
    )
    db.add(booking)
    db.flush()
    return booking

def test_availability():
    # Use real Postgres engine for testing
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        host, guest, prop1, prop2, offer = setup_test_data(db)
        
        # Test 1: Property 1 (inventory 1), no bookings -> Available
        avail = is_property_available(db, prop1.id, date(2026, 4, 1), date(2026, 4, 10))
        assert avail == True, "Test 1 Failed"
        print("Test 1 Passed: Property with no bookings is available.")
        
        # Create booking for Property 1: April 5 - 15
        create_booking(db, prop1.id, offer.id, guest.id, host.id, date(2026, 4, 5), date(2026, 4, 15))
        
        # Test 2: Property 1, query April 1 - 4 -> Available (No overlap)
        avail = is_property_available(db, prop1.id, date(2026, 4, 1), date(2026, 4, 4))
        assert avail == True, "Test 2 Failed"
        print("Test 2 Passed: Non-overlapping earlier dates -> Available.")
        
        # Test 3: Property 1, query April 15 - 20 -> Available (No overlap, checkout matches checkin)
        avail = is_property_available(db, prop1.id, date(2026, 4, 15), date(2026, 4, 20))
        assert avail == True, "Test 3 Failed"
        print("Test 3 Passed: Non-overlapping later dates -> Available.")
        
        # Test 4: Property 1, query April 10 - 20 -> Overlap! -> Not Available
        avail = is_property_available(db, prop1.id, date(2026, 4, 10), date(2026, 4, 20))
        assert avail == False, "Test 4 Failed"
        print("Test 4 Passed: Overlapping dates (inventory 1) -> Not Available.")

        # Test 5: Property 2 (inventory 2), no bookings
        create_booking(db, prop2.id, offer.id, guest.id, host.id, date(2026, 4, 5), date(2026, 4, 15))
        
        # Query Property 2 for April 10 - 20 -> Overlap, but inventory is 2 -> Available!
        avail = is_property_available(db, prop2.id, date(2026, 4, 10), date(2026, 4, 20))
        assert avail == True, "Test 5 Failed"
        print("Test 5 Passed: Overlapping dates but inventory 2 -> Available.")
        
        # Test 6: Create second booking for Property 2: April 10 - 12
        create_booking(db, prop2.id, offer.id, guest.id, host.id, date(2026, 4, 10), date(2026, 4, 12))
        
        # Query Property 2 for April 6 - 13 -> Overlaps with both bookings! (count=2, inv=2 -> False)
        avail = is_property_available(db, prop2.id, date(2026, 4, 6), date(2026, 4, 13))
        assert avail == False, "Test 6 Failed"
        print("Test 6 Passed: Two overlapping bookings max out inventory 2 -> Not Available.")
        
        print("\nAll Availability Service tests passed successfully!")
        
    except Exception as e:
        import traceback
        with open("traceback_output.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print(f"Error during test: {e}")
    finally:
        # Rollback so we don't save the test data to the real DB
        db.rollback()
        db.close()

if __name__ == "__main__":
    test_availability()
