"""
test_search.py

Functional test for the Search Service.
Verifies that structural, availability, and economic filtering work together.
"""

from datetime import date, timedelta, datetime, timezone
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, engine
from app.models import User, City, Property, PropertyOfferFilter, Booking, Offer
from app.models.enums import UserRole, PropertyType, PricingMode, OfferStatus
from app.services.search_service import search_available_properties

def setup_test_data(db):
    print("Setting up search test data...")
    # Create test host and guest
    host = User(
        name="Test Search Host",
        email="test_search_host@example.com",
        password_hash="fakehash",
        role=UserRole.host
    )
    guest = User(
        name="Test Search Guest",
        email="test_search_guest@example.com",
        password_hash="fakehash",
        role=UserRole.guest
    )
    db.add_all([host, guest])
    db.flush()

    # Create dummy city
    city = City(
        name="Search City",
        province="Test Province",
        property_count=4
    )
    db.add(city)
    db.flush()

    # --- Property 1: Perfect match ---
    # Max guests 4, base min nights 1
    prop1 = Property(
        host_id=host.id, city_id=city.id, title="Perfect Property",
        property_type=PropertyType.apartment, inventory_count=1,
        max_guests=4, room_count=2, pets_allowed=False,
        children_allowed=True, pool_available=False,
        price_reference=10000, base_min_nights=1, is_active=True
    )
    db.add(prop1)
    
    # --- Property 2: Fails max_guests structural filter ---
    prop2 = Property(
        host_id=host.id, city_id=city.id, title="Small Property",
        property_type=PropertyType.apartment, inventory_count=1,
        max_guests=1, room_count=1, pets_allowed=False, # <-- Max guests is 1
        children_allowed=False, pool_available=False,
        price_reference=5000, base_min_nights=1, is_active=True
    )
    db.add(prop2)
    
    # --- Property 3: Fails availability filter (Booked) ---
    prop3 = Property(
        host_id=host.id, city_id=city.id, title="Booked Property",
        property_type=PropertyType.apartment, inventory_count=1,
        max_guests=4, room_count=2, pets_allowed=True,
        children_allowed=True, pool_available=True,
        price_reference=15000, base_min_nights=1, is_active=True
    )
    db.add(prop3)
    
    # --- Property 4: Fails economic filter (min_nights is 7) ---
    prop4 = Property(
        host_id=host.id, city_id=city.id, title="Long-stay Property",
        property_type=PropertyType.apartment, inventory_count=1,
        max_guests=4, room_count=2, pets_allowed=True,
        children_allowed=True, pool_available=True,
        price_reference=10000, base_min_nights=1, is_active=True
    )
    db.add(prop4)
    db.flush()

    # Economic filters
    # Prop 1: $10,000 / night for stays 1+ nights
    db.add(PropertyOfferFilter(property_id=prop1.id, min_nights=1, price_per_night=10000))
    # Prop 2: $5,000 / night for stays 1+ nights
    db.add(PropertyOfferFilter(property_id=prop2.id, min_nights=1, price_per_night=5000))
    # Prop 3: $15,000 / night for stays 1+ nights
    db.add(PropertyOfferFilter(property_id=prop3.id, min_nights=1, price_per_night=15000))
    # Prop 4: $8,000 / night for stays 7+ nights ONLY
    db.add(PropertyOfferFilter(property_id=prop4.id, min_nights=7, price_per_night=8000))
    db.flush()

    # Dummy offer for foreign key (so we can create a booking for prop3)
    offer = Offer(
        guest_id=guest.id, city_id=city.id, checkin_date=date(2026, 4, 1),
        checkout_date=date(2026, 4, 30), nights=30, guest_count=2,
        pricing_mode=PricingMode.nightly_rate, offered_price_per_night=15000,
        offered_total_amount=450000, duration_hours=24,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1), status=OfferStatus.active
    )
    db.add(offer)
    db.flush()

    # Booking for Prop 3 covering April 5 to 15
    booking = Booking(
        offer_id=offer.id, property_id=prop3.id, guest_id=guest.id,
        host_id=host.id, checkin_date=date(2026, 4, 5), checkout_date=date(2026, 4, 15),
        nights=10, price_per_night=15000, total_amount=150000
    )
    db.add(booking)
    db.flush()

    return city

def test_search():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        city = setup_test_data(db)
        
        print("\nExecuting Search...")
        # Searching for April 10 to April 15 (5 nights), for 2 guests
        checkin = date(2026, 4, 10)
        checkout = date(2026, 4, 15)
        guest_count = 2
        
        results = search_available_properties(db, city.id, checkin, checkout, guest_count)
        
        print(f"Search returned {len(results)} properties. (Expected: 1)")
        
        # Analyze results
        found_properties = [r["property"].title for r in results]
        print(f"Found titles: {found_properties}")
        
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0]["property"].title == "Perfect Property", "Wrong property was returned."
        assert results[0]["effective_threshold"] == 10000, "Wrong effective threshold for Perfect Property."
        
        print("\nAll Search tests passed successfully! Components are orchestrating correctly.")
        
    except Exception as e:
        import traceback
        with open("traceback_search.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print(f"Error during test: {e}")
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    test_search()
