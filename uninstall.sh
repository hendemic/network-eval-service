#!/bin/bash
# Network Evaluation Service - Uninstall Script
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default installation directory
INSTALL_DIR="/opt/network-evaluation-service"

# Print header
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Network Evaluation Service Uninstaller   ${NC}"
echo -e "${GREEN}============================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run this script as root or with sudo${NC}"
  exit 1
fi

# Function to display progress
progress() {
  echo -e "${YELLOW}➤ $1${NC}"
}

# Function to display success
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Confirm uninstallation
echo -e "${RED}WARNING: This will completely remove Network Evaluation Service and all its data.${NC}"
read -p "Are you sure you want to continue? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo -e "${YELLOW}Uninstallation cancelled.${NC}"
  exit 0
fi

# Custom installation location
read -p "Enter installation directory [$INSTALL_DIR]: " CUSTOM_DIR
INSTALL_DIR=${CUSTOM_DIR:-$INSTALL_DIR}

# Check if directory exists
if [ ! -d "$INSTALL_DIR" ]; then
  echo -e "${RED}Could not find $INSTALL_DIR. Exiting.${NC}"
  exit 1
fi

# Stop and remove containers, networks, and volumes
if [ -f "$INSTALL_DIR/docker-compose.yml" ]; then
  progress "Stopping and removing Docker containers, networks, and volumes..."
  cd "$INSTALL_DIR"
  
  # The -v flag removes volumes defined in the compose file
  docker compose down -v
  
  # Get the directory name for container prefix (used by docker-compose)
  DIR_NAME=$(basename "$INSTALL_DIR")
  
  # Remove specific containers if they still exist
  progress "Checking for remaining containers..."
  for CONTAINER in "${DIR_NAME}-db-1" "${DIR_NAME}-web-1" "${DIR_NAME}-test-1" "${DIR_NAME}-db-init-1"; do
    if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER$"; then
      echo "Removing container: $CONTAINER"
      docker rm -f "$CONTAINER"
    fi
  done
  
  # Remove the specific volume
  progress "Checking for remaining volumes..."
  if docker volume ls --format '{{.Name}}' | grep -q "^${DIR_NAME}_postgres_data$"; then
    echo "Removing volume: ${DIR_NAME}_postgres_data"
    docker volume rm "${DIR_NAME}_postgres_data"
  fi
  
  # Also check for any other volumes with a similar name pattern
  OTHER_VOLUMES=$(docker volume ls --format '{{.Name}}' | grep "network.*evaluation.*postgres")
  if [ ! -z "$OTHER_VOLUMES" ]; then
    echo "Removing other related volumes:"
    for VOL in $OTHER_VOLUMES; do
      echo "  - $VOL"
      docker volume rm "$VOL"
    done
  fi
  
  success "Docker resources removed"
fi

# Remove bash shortcuts
progress "Removing command shortcuts..."
if [ -f "/usr/local/bin/nes-update" ]; then
  rm -f /usr/local/bin/nes-update
  echo "Removed nes-update command"
fi

if [ -f "/usr/local/bin/nes-remove" ]; then
  rm -f /usr/local/bin/nes-remove
  echo "Removed nes-remove command"
fi
success "Command shortcuts removed"

# Remove the installation directory
progress "Removing installation directory..."
rm -rf "$INSTALL_DIR"
success "Installation directory removed"

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}    Uninstallation completed successfully!  ${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "\nNetwork Evaluation Service has been completely removed from your system."