#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS network_eval;
    GRANT ALL ON SCHEMA network_eval TO $POSTGRES_USER;
    GRANT USAGE ON SCHEMA public TO $POSTGRES_USER;
    GRANT CREATE ON SCHEMA public TO $POSTGRES_USER;
    
    CREATE TABLE IF NOT EXISTS public.alembic_version (
        version_num VARCHAR(32) NOT NULL, 
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
    );
    GRANT ALL ON TABLE public.alembic_version TO $POSTGRES_USER;
EOSQL