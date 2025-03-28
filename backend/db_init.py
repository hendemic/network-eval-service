from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
import os
import subprocess

from models import db
from config import config

def init_db():
    # Create a minimal Flask app
    app = Flask(__name__)
    app.config.from_object(config['default'])
    
    # Initialize extensions
    db.init_app(app)
    migrate_manager = Migrate(app, db)
    
    with app.app_context():
        # Create database if it doesn't exist
        try:
            # Check if the database exists
            subprocess.run([
                "psql", 
                "-h", app.config['POSTGRES_HOST'],
                "-U", app.config['POSTGRES_USER'],
                "-p", app.config['POSTGRES_PORT'],
                "-d", "postgres",
                "-c", f"SELECT 1 FROM pg_database WHERE datname = '{app.config['POSTGRES_DB']}'"
            ], check=True, capture_output=True, env={"PGPASSWORD": app.config['POSTGRES_PASSWORD']})
            
            print(f"Database '{app.config['POSTGRES_DB']}' already exists.")
        except subprocess.CalledProcessError:
            # Create the database
            subprocess.run([
                "psql",
                "-h", app.config['POSTGRES_HOST'],
                "-U", app.config['POSTGRES_USER'],
                "-p", app.config['POSTGRES_PORT'],
                "-d", "postgres",
                "-c", f"CREATE DATABASE {app.config['POSTGRES_DB']}"
            ], check=True, env={"PGPASSWORD": app.config['POSTGRES_PASSWORD']})
            
            print(f"Created database '{app.config['POSTGRES_DB']}'.")
            
        # Initialize migrations if needed
        if not os.path.exists('migrations'):
            print("Initializing migrations directory...")
            init()
            
        # Create initial migration
        print("Creating migration...")
        migrate()
        
        # Apply migration
        print("Applying migration...")
        upgrade()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()