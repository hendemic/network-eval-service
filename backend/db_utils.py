#!/usr/bin/env python3
"""
Simplified utility script to help with database setup.
"""
import subprocess
import os
import sys

# Add parent directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import config

def setup_db():
    """
    Set up database and schema for the application.
    """
    # Get configuration
    db_config = config['default']
    
    # Database connection info with no password in output
    conn_info = f"host={db_config.POSTGRES_HOST} port={db_config.POSTGRES_PORT} user={db_config.POSTGRES_USER}"
    print(f"Setting up database using: {conn_info}")
    
    # Set password for PostgreSQL commands
    os.environ["PGPASSWORD"] = db_config.POSTGRES_PASSWORD
    
    try:
        # 1. Check if database exists
        print(f"Checking if database '{db_config.POSTGRES_DB}' exists...")
        db_exists = subprocess.run(
            ["psql", "-h", db_config.POSTGRES_HOST, "-U", db_config.POSTGRES_USER, 
             "-p", db_config.POSTGRES_PORT, "-d", "postgres", "-tAc", 
             f"SELECT 1 FROM pg_database WHERE datname='{db_config.POSTGRES_DB}'"],
            capture_output=True, text=True
        ).stdout.strip() == "1"
        
        # 2. Create database if it doesn't exist
        if not db_exists:
            print(f"Creating database '{db_config.POSTGRES_DB}'...")
            subprocess.run(
                ["psql", "-h", db_config.POSTGRES_HOST, "-U", db_config.POSTGRES_USER, 
                 "-p", db_config.POSTGRES_PORT, "-d", "postgres", "-c", 
                 f"CREATE DATABASE {db_config.POSTGRES_DB}"],
                check=True
            )
            print(f"Database '{db_config.POSTGRES_DB}' created successfully!")
        else:
            print(f"Database '{db_config.POSTGRES_DB}' already exists.")
            
        # 3. Create schema in the database
        print(f"Creating schema '{db_config.POSTGRES_SCHEMA}'...")
        subprocess.run(
            ["psql", "-h", db_config.POSTGRES_HOST, "-U", db_config.POSTGRES_USER, 
             "-p", db_config.POSTGRES_PORT, "-d", db_config.POSTGRES_DB, "-c", 
             f"CREATE SCHEMA IF NOT EXISTS {db_config.POSTGRES_SCHEMA}"],
            check=True
        )
        print(f"Schema '{db_config.POSTGRES_SCHEMA}' created or already exists.")
        
        print("Database setup completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up database: {e}")
        print(f"Command output: {e.output if hasattr(e, 'output') else 'No output'}")
        return False

if __name__ == "__main__":
    setup_db()