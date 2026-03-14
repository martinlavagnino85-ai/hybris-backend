"""
database.py

This module configures the connection to the PostgreSQL database using SQLAlchemy.

Responsibilities:
- Loading the database connection URL from environment variables.
- Creating the centralized SQLAlchemy engine to communicate with the database.
- Defining the declarative Base class that all ORM models will inherit from.

Why it exists:
To establish a single, robust connection point between the FastAPI application and the PostgreSQL database, avoiding scattered connection logic.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# The application uses python-dotenv to load environment variables from the .env file.
# The URL must point to a PostgreSQL database.
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/hybris"
)

# Create the SQLAlchemy engine which is the starting point for any SQLAlchemy application.
# It acts as a central source of connections to a particular database.
engine = create_engine(DATABASE_URL)

# Create the declarative base. 
# All of our database models (Users, Properties, etc.) will inherit from this Base class
# so SQLAlchemy knows they represent tables in the database.
Base = declarative_base()
