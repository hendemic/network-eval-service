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
        
        # SQLAlchemy 2.x compatible way to get table names
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        print(f"Created tables: {inspector.get_table_names(schema=app.config.get('POSTGRES_SCHEMA', 'network_eval'))}")
        print("Database initialization successful!")
except Exception as e:
    print(f"Database initialization error: {str(e)}", file=sys.stderr)
    sys.exit(1)