#!/usr/bin/env python3
"""
Simple database initialization script that bypasses Alembic.
"""
from flask import Flask
import os
import sys

# Add parent directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, PingResult
from backend.config import config

def init_db():
    """Initialize the database by directly creating tables using SQLAlchemy."""
    # Create a minimal Flask app
    app = Flask(__name__)
    app.config.from_object(config['default'])
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create all tables directly
    with app.app_context():
        print("Creating database tables directly with SQLAlchemy...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Verify tables were created
        if PingResult.__table__ in db.metadata.tables.values():
            print(f"✓ Table '{PingResult.__tablename__}' exists in schema '{config['default'].POSTGRES_SCHEMA}'")
        else:
            print(f"✗ Failed to create table '{PingResult.__tablename__}'")

if __name__ == '__main__':
    init_db()