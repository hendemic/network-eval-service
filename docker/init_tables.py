#!/usr/bin/env python3
import sys
import os

# Add parent directory to path so imports work correctly
sys.path.append('/app')

from backend.models import db, PingResult
from backend.app import create_app

try:
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print(f"Created tables: {db.engine.table_names()}")
        print("Database initialization successful!")
except Exception as e:
    print(f"Database initialization error: {str(e)}", file=sys.stderr)
    sys.exit(1)