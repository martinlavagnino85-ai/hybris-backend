"""
test_economic.py

Script to test the economic logic service against a local Postgres database.
"""

from datetime import date
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, engine
from app.models import User, City, Property, PropertyOfferFilter
from app.models.enums import UserRole, PropertyType, PricingMode
from app.services.economic_service import calculate_nights, calculate_effective_threshold, convert_rate

def setup_test_data(db):
    print("Setting up test data...")
    # Create test host
    host = User(
        name="Test Eco Host",
        email="test_eco_host@example.com",
        password_hash="fakehash",
        role=UserRole.host
    )
    db.add(host)
    db.flush()

    # Create dummy city
    city = City(
        name="Economic City",
        province="Test Province",
        property_count=1
    )
    db.add(city)
    db.flush()

    # Create property
    prop = Property(
        host_id=host.id,
        city_id=city.id,
        title="Economic Test Property",
        property_type=PropertyType.apartment,
        inventory_count=1,
        max_guests=2,
        room_count=1,
        pets_allowed=False,
        children_allowed=True,
        pool_available=False,
        price_reference=1000,
        base_min_nights=1
    )
    db.add(prop)
    db.flush()
    
    # Create pricing filters for property
    # 1 night minimum: $25000 per night
    filter1 = PropertyOfferFilter(
        property_id=prop.id,
        min_nights=1,
        price_per_night=25000
    )
    db.add(filter1)
    
    # 3 nights minimum: $20000 per night
    filter2 = PropertyOfferFilter(
        property_id=prop.id,
        min_nights=3,
        price_per_night=20000
    )
    db.add(filter2)

    # 7 nights minimum: $15000 per night
    filter3 = PropertyOfferFilter(
        property_id=prop.id,
        min_nights=7,
        price_per_night=15000
    )
    db.add(filter3)
    db.flush()

    return prop

def test_economic_logic():
    # Use real Postgres engine for testing
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        prop = setup_test_data(db)
        
        print("Testing calculate_nights...")
        # Checkin April 1, Checkout April 5 = 4 nights
        assert calculate_nights(date(2026, 4, 1), date(2026, 4, 5)) == 4
        # Same day checkin/checkout = 0 nights
        assert calculate_nights(date(2026, 4, 1), date(2026, 4, 1)) == 0
        # Checkin after checkout = 0 nights
        assert calculate_nights(date(2026, 4, 5), date(2026, 4, 1)) == 0
        print("calculate_nights tests passed.")
        
        print("\nTesting calculate_effective_threshold...")
        
        # Test 1: Requested 1 night -> Only filter1 qualifies -> Threshold: $25000
        t1 = calculate_effective_threshold(db, prop.id, 1)
        assert t1 == 25000, f"Expected 25000, got {t1}"
        
        # Test 2: Requested 2 nights -> Only filter1 qualifies -> Threshold: $25000
        t2 = calculate_effective_threshold(db, prop.id, 2)
        assert t2 == 25000, f"Expected 25000, got {t2}"
        
        # Test 3: Requested 3 nights -> filter1 & filter2 qualify -> MIN(25000, 20000) -> Threshold: $20000
        t3 = calculate_effective_threshold(db, prop.id, 3)
        assert t3 == 20000, f"Expected 20000, got {t3}"
        
        # Test 4: Requested 5 nights -> filter1 & filter2 qualify -> MIN(25000, 20000) -> Threshold: $20000
        t4 = calculate_effective_threshold(db, prop.id, 5)
        assert t4 == 20000, f"Expected 20000, got {t4}"
        
        # Test 5: Requested 10 nights -> All filters qualify -> MIN(25000, 20000, 15000) -> Threshold: $15000
        t5 = calculate_effective_threshold(db, prop.id, 10)
        assert t5 == 15000, f"Expected 15000, got {t5}"
        
        print("calculate_effective_threshold tests passed.")
        
        print("\nTesting convert_rate...")
        # Test same mode -> no change
        assert convert_rate(1000, 5, PricingMode.nightly_rate, PricingMode.nightly_rate) == 1000
        assert convert_rate(5000, 5, PricingMode.total_budget, PricingMode.total_budget) == 5000
        
        # Test rate to total
        assert convert_rate(1000, 5, PricingMode.nightly_rate, PricingMode.total_budget) == 5000
        
        # Test total to rate 
        assert convert_rate(6000, 3, PricingMode.total_budget, PricingMode.nightly_rate) == 2000
        
        # Edge cases 
        assert convert_rate(1000, 0, PricingMode.nightly_rate, PricingMode.total_budget) == 0
        
        print("convert_rate tests passed.")
        
        print("\nAll Economic Logic tests passed successfully!")
        
    except Exception as e:
        import traceback
        with open("traceback_economic.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print(f"Error during test: {e}")
    finally:
        # Rollback so we don't save the test data to the real DB
        db.rollback()
        db.close()

if __name__ == "__main__":
    test_economic_logic()
