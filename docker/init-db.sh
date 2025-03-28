#!/bin/bash
set -e

# Display current database configuration
echo "Initializing database with:"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "POSTGRES_SCHEMA: network_eval"

# Set up schema and permissions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create schema if it doesn't exist
    CREATE SCHEMA IF NOT EXISTS network_eval;
    
    -- Grant permissions
    GRANT ALL ON SCHEMA network_eval TO $POSTGRES_USER;
    GRANT USAGE ON SCHEMA public TO $POSTGRES_USER;
    GRANT CREATE ON SCHEMA public TO $POSTGRES_USER;
    
    -- Create alembic_version table for migrations
    CREATE TABLE IF NOT EXISTS public.alembic_version (
        version_num VARCHAR(32) NOT NULL, 
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
    );
    GRANT ALL ON TABLE public.alembic_version TO $POSTGRES_USER;
    
    -- Set search path to include our schema
    ALTER ROLE $POSTGRES_USER SET search_path TO network_eval, public;
EOSQL

echo "Database initialization completed successfully"