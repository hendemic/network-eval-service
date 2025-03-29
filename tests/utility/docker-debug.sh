#!/bin/bash
# Debug script for Docker deployment issues

echo "====== Docker Container Status ======"
docker compose ps

echo -e "\n====== Docker Compose Configuration ======"
grep -v "^#" docker-compose.yml | grep -v "^$"

echo -e "\n====== Environment Variables (.env) ======"
if [ -f ".env" ]; then
    grep -v "^#" .env | grep -v "^$"
else
    echo "No .env file found. Using default values from docker-compose.yml."
fi

echo -e "\n====== Web Container Logs ======"
docker compose logs web | tail -n 30

echo -e "\n====== Database Container Logs ======"
docker compose logs db | tail -n 30

echo -e "\n====== Database Initialization Logs ======"
docker compose logs db-init | tail -n 30

echo -e "\n====== Test Container Logs ======"
docker compose logs test | tail -n 30

echo -e "\n====== Database Connection Test ======"
docker compose exec -T web python -c "
from backend.models import db, PingResult
from backend.app import create_app
try:
    app = create_app()
    with app.app_context():
        print(f'Connected to database. Tables: {db.engine.table_names()}')
        count = PingResult.query.count()
        print(f'Records in PingResult table: {count}')
except Exception as e:
    print(f'Error: {str(e)}')
" || echo "Failed to connect to web container. Is it running?"

echo -e "\n====== Database Schema Check ======"
docker compose exec -T db psql -U "${POSTGRES_USER:-netmon}" -d "${POSTGRES_DB:-network_tests}" -c "\dn" || echo "Failed to check database schemas"

echo -e "\n====== Database Tables Check ======"
docker compose exec -T db psql -U "${POSTGRES_USER:-netmon}" -d "${POSTGRES_DB:-network_tests}" -c "\dt network_eval.*" || echo "Failed to check database tables"