#!/usr/bin/env python3
"""
Database debug script to check connection and verify tables
"""
import sys
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Get database connection parameters from environment
db_user = os.environ.get('POSTGRES_USER', 'netmon')
db_pass = os.environ.get('POSTGRES_PASSWORD', 'netmon')
db_host = os.environ.get('POSTGRES_HOST', 'db')
db_port = os.environ.get('POSTGRES_PORT', '5432')
db_name = os.environ.get('POSTGRES_DB', 'network_tests')
db_schema = os.environ.get('POSTGRES_SCHEMA', 'network_eval')

print(f"Attempting to connect to database:")
print(f"  Host: {db_host}:{db_port}")
print(f"  Database: {db_name}")
print(f"  Schema: {db_schema}")
print(f"  User: {db_user}")

# Construct database URL
db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
print(f"Database URL: {db_url.replace(db_pass, '******')}")

# Try to connect to the database
max_retries = 5
retry_delay = 3

for attempt in range(max_retries):
    try:
        print(f"\nAttempt {attempt+1}/{max_retries} to connect to database")
        
        # Create engine and connect
        engine = create_engine(db_url)
        conn = engine.connect()
        
        # List all schemas
        print("Available schemas:")
        schemas = conn.execute("SELECT schema_name FROM information_schema.schemata").fetchall()
        for schema in schemas:
            print(f"  - {schema[0]}")
        
        # Check if our schema exists
        schema_exists = conn.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = %s)",
            (db_schema,)
        ).scalar()
        
        if schema_exists:
            print(f"Schema '{db_schema}' exists")
            
            # List tables in our schema
            print(f"Tables in '{db_schema}' schema:")
            tables = conn.execute(
                f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{db_schema}'"
            ).fetchall()
            
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
                print("Database connection and schema verification successful!")
            else:
                print(f"No tables found in schema '{db_schema}'")
                print("Schema exists but no tables - table creation may have failed")
        else:
            print(f"Schema '{db_schema}' does not exist!")
            print("Schema creation failed or using wrong schema name")
        
        # Close connection
        conn.close()
        break
        
    except OperationalError as e:
        print(f"Database connection error on attempt {attempt+1}: {str(e)}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Maximum retries reached. Database connection failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)