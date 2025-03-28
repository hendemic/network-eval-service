#!/usr/bin/env python3
"""
Utility script to help with database permission issues.
This script should be run by a superuser (postgres) to grant the necessary permissions.
"""

import argparse
import subprocess
import os
from config import config

def setup_db_permissions():
    """
    Set up database permissions for the application user.
    This script should be run as the postgres superuser.
    """
    # Get configuration
    db_config = config['default']
    
    # Create database if it doesn't exist
    try:
        subprocess.run([
            "psql",
            "-c", f"SELECT 1 FROM pg_database WHERE datname = '{db_config.POSTGRES_DB}'"
        ], check=True, capture_output=True)
        
        print(f"Database '{db_config.POSTGRES_DB}' already exists.")
    except subprocess.CalledProcessError:
        subprocess.run([
            "psql",
            "-c", f"CREATE DATABASE {db_config.POSTGRES_DB}"
        ], check=True)
        
        print(f"Created database '{db_config.POSTGRES_DB}'.")
    
    # Connect to the database and set up permissions
    subprocess.run([
        "psql",
        "-d", db_config.POSTGRES_DB,
        "-c", f"CREATE SCHEMA IF NOT EXISTS {db_config.POSTGRES_SCHEMA};"
    ], check=True)
    
    print(f"Created schema '{db_config.POSTGRES_SCHEMA}' if it didn't exist.")
    
    # Grant permissions to the application user
    subprocess.run([
        "psql",
        "-d", db_config.POSTGRES_DB,
        "-c", f"GRANT ALL ON SCHEMA {db_config.POSTGRES_SCHEMA} TO {db_config.POSTGRES_USER};"
    ], check=True)
    
    # Grant permissions for migrations
    subprocess.run([
        "psql",
        "-d", db_config.POSTGRES_DB,
        "-c", f"GRANT CREATE ON SCHEMA {db_config.POSTGRES_SCHEMA} TO {db_config.POSTGRES_USER};"
    ], check=True)
    
    # Grant usage on the public schema for alembic_version table
    subprocess.run([
        "psql",
        "-d", db_config.POSTGRES_DB,
        "-c", f"GRANT USAGE ON SCHEMA public TO {db_config.POSTGRES_USER};"
    ], check=True)
    
    # Grant create on public schema for alembic_version table
    subprocess.run([
        "psql",
        "-d", db_config.POSTGRES_DB,
        "-c", f"GRANT CREATE ON SCHEMA public TO {db_config.POSTGRES_USER};"
    ], check=True)
    
    # Create alembic_version table ahead of time if it doesn't exist
    try:
        subprocess.run([
            "psql",
            "-d", db_config.POSTGRES_DB,
            "-c", "CREATE TABLE IF NOT EXISTS public.alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num));"
        ], check=True)
        
        # Grant permissions on the alembic_version table
        subprocess.run([
            "psql",
            "-d", db_config.POSTGRES_DB,
            "-c", f"GRANT ALL ON TABLE public.alembic_version TO {db_config.POSTGRES_USER};"
        ], check=True)
        
        print("Created alembic_version table and granted permissions.")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not create alembic_version table: {e}")
    
    print(f"Granted necessary permissions to user '{db_config.POSTGRES_USER}'.")
    print("The application should now be able to create tables and run migrations.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up database permissions for the Network Evaluation Service")
    parser.add_argument("--confirm", action="store_true", help="Confirm that you want to set up permissions")
    
    args = parser.parse_args()
    
    if args.confirm:
        setup_db_permissions()
    else:
        print("Please run with --confirm to apply the changes.")
        print("Note: This script should be run as the postgres superuser.")
        print("Example: sudo -u postgres python db_utils.py --confirm")