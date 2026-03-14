"""
session.py

This module manages database sessions for the application.

Responsibilities:
- Creating a sessionmaker factory configured to use our SQLAlchemy engine.
- Providing a dependency injection function (`get_db`) to be used by FastAPI endpoints.

Why it exists:
To ensure that each API request gets its own independent database session. 
This prevents data bleed between requests and ensures that connections are properly closed when a request finishes.
"""

from sqlalchemy.orm import sessionmaker
from app.db.database import engine

# Create a factory for generating new database sessions.
# - autocommit=False: We manually control when to commit transactions to the database.
# - autoflush=False: We manually control when to flush changes to the database.
# - bind=engine: We connect these sessions to the central engine defined in database.py.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function to generate a new database session for a single request.
    
    This function uses the 'yield' keyword to provide a session to an endpoint,
    and then ensures the session is safely closed after the endpoint finishes processing
    (even if an error occurs during processing).
    
    Parameters:
    None. It relies on the SessionLocal factory.
    
    Returns:
    A SQLAlchemy Session object that can be used to query or modify the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
