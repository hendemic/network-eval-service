#!/bin/bash
# Network Evaluation Service - Update Script
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Network Evaluation Service Updater       ${NC}"
echo -e "${GREEN}============================================${NC}"

# Function to display progress
progress() {
  echo -e "${YELLOW}➤ $1${NC}"
}

# Function to display success
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Stop existing containers
progress "Stopping existing containers..."
docker compose down
success "Containers stopped"

# Pull latest changes
progress "Pulling latest changes from repository..."
git pull
success "Repository updated"

# Rebuild and start containers
progress "Rebuilding and starting containers..."
docker compose up -d --build
success "Containers rebuilt and started"

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}    Update completed successfully!          ${NC}"
echo -e "${GREEN}============================================${NC}"

HOST_IP=$(hostname -I | awk '{print $1}')
WEB_PORT=$(grep "WEB_PORT" .env 2>/dev/null | cut -d '=' -f2 || echo "5000")

echo -e "\nYou can access the web dashboard at: ${YELLOW}http://$HOST_IP:$WEB_PORT${NC}"
echo -e "\nUseful commands:"
echo -e "  - View logs: ${YELLOW}docker compose logs -f${NC}"
echo -e "  - Restart services: ${YELLOW}docker compose restart${NC}"