"""
main.py

This is the entry point for the Hybris backend application.

Responsibilities:
- Initializing the FastAPI application.
- Loading environment variables (like the database connection string) from the .env file.
- Including all the routers that define the API endpoints.

Why it exists:
This file serves as the core orchestrator. When the server starts, it runs this file
to set up the entire application environment before accepting any HTTP requests from users.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file into the system's environment
# This must happen before we initialize components that rely on these variables (like the database).
load_dotenv()

from fastapi import FastAPI
# Note: we import our database components here to ensure they initialize properly
from app.db.database import engine, Base

# Initialize the FastAPI application instance
app = FastAPI(
    title="Hybris Backend API",
    description="Demand-driven temporary rental marketplace where guests propose a price and hosts compete.",
    version="1.0.0"
)

# Create all tables in the database. 
# This relies on the Base metadata and the engine.
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    """
    A simple health check endpoint to confirm the server is running.
    
    Parameters:
    None
    
    Returns:
    dict: A welcome message indicating the API is active.
    """
    return {"message": "Welcome to the Hybris Backend API"}

# At this stage, routers will be included later as we implement the various services.
"""
Example placeholder for when we include routers in future steps:
from app.routers import search_router, offer_router, host_router, city_router
app.include_router(search_router.router, prefix="/search", tags=["Search"])
...
"""
