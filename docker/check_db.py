#!/usr/bin/env python3
import sys
import os
import time
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError

# Get database details
db_user = os.environ.get("POSTGRES_USER", "netmon")
db_pass = os.environ.get("POSTGRES_PASSWORD", "netmon")
db_host = os.environ.get("POSTGRES_HOST", "db")
db_port = os.environ.get("POSTGRES_PORT", "5432")
db_name = os.environ.get("POSTGRES_DB", "network_tests")

print(f"Checking connection to {db_host}:{db_port}/{db_name} as {db_user}")
db_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Try to connect
max_retries = 5
retry_delay = 3

for attempt in range(max_retries):
    try:
        engine = sa.create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(sa.text("SELECT 1")).scalar()
            print(f"Connection successful! Result: {result}")
            break
    except OperationalError as e:
        print(f"Attempt {attempt+1}/{max_retries} failed: {str(e)}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("All connection attempts failed")
            sys.exit(1)