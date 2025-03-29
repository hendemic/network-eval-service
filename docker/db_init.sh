#!/bin/bash
# Database initialization script for the db-init service

set -e

echo "Waiting for database to be fully ready..."
sleep 10
echo "Starting database initialization..."
echo "Current working directory: $(pwd)"
echo "Listing /app directory:"
ls -la /app

# Check for Python modules
echo "Checking Python modules:"
python -c "import sys; print('Python modules path:'); print('\n'.join(sys.path))"

# Run the database connection check
echo "Running database connection check..."
python /app/docker/check_db.py

# If connection check was successful, initialize tables
if [ $? -eq 0 ]; then
    echo "Database connection successful, initializing tables..."
    
    # Print environment variables for debugging
    echo "Environment variables for database connection:"
    env | grep POSTGRES

    # Run the table initialization script
    python /app/docker/init_tables.py
    
    if [ $? -eq 0 ]; then
        echo "Database tables created successfully!"
    else
        echo "Failed to create database tables."
        exit 2
    fi
else
    echo "Database connection failed, cannot initialize tables."
    exit 1
fi

echo "Database initialization process completed."