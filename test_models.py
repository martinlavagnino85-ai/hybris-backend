from app.db.database import Base, engine
from app.models import *

def test_models():
    Base.metadata.create_all(bind=engine)
    print("Models generated successfully.")

if __name__ == "__main__":
    test_models()
