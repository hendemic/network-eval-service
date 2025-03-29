#!/bin/bash
# Database initialization script for the db-init service

set -e

echo "Waiting for database to be fully ready..."
sleep 5
echo "Starting database initialization..."

# Run the database connection check
python /app/docker/check_db.py

# If connection check was successful, initialize tables
if [ $? -eq 0 ]; then
    echo "Database connection successful, initializing tables..."
    python /app/docker/init_tables.py
else
    echo "Database connection failed, cannot initialize tables."
    exit 1
fi

echo "Database initialization process completed."