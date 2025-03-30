#!/bin/bash
# Network Evaluation Service - Docker Installation Script
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Repository URL
REPO_URL="https://github.com/hendemic/network-eval-service.git"

# Default installation directory
INSTALL_DIR="/opt/network-evaluation-service"

# Print header
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Network Evaluation Service Installer     ${NC}"
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

# Function to check for required tools
check_requirements() {
  progress "Checking requirements..."

  # Check if Docker is installed
  if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
  fi

  # Check if Docker Compose is installed
  if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose plugin is not installed. Installing Docker Compose...${NC}"
    apt-get update
    apt-get install -y docker-compose-plugin
  fi

  # Verify docker is running
  if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Starting Docker...${NC}"
    systemctl start docker
  fi

  success "All requirements satisfied"
}

# 1. Check requirements
check_requirements

# 2. Clone the repository
# Choose between production and development branch
DEFAULT_BRANCH="production"
read -p "Which branch do you want to install? [production/development] (default: production): " BRANCH_CHOICE
BRANCH=${BRANCH_CHOICE:-$DEFAULT_BRANCH}

# Convert "development" to "main" for git operations
if [ "$BRANCH" = "development" ]; then
  GIT_BRANCH="main"
  BRANCH_NAME="development"
else
  GIT_BRANCH="production"
  BRANCH_NAME="production"
fi

progress "Cloning repository from $REPO_URL ($BRANCH_NAME branch)..."
if [ -d "$INSTALL_DIR" ]; then
  echo -e "${YELLOW}Directory already exists. Updating...${NC}"
  cd "$INSTALL_DIR"
  git fetch
  git checkout $GIT_BRANCH
  git pull origin $GIT_BRANCH
else
  git clone -b $GIT_BRANCH $REPO_URL "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi
success "Repository cloned successfully ($BRANCH_NAME branch)"

# 3. Configure environment variables
progress "Configuring environment variables..."
if [ -f "$INSTALL_DIR/.env" ]; then
  echo -e "${YELLOW}Environment file already exists.${NC}"
  read -p "Do you want to keep the existing configuration? (Y/n): " KEEP_ENV
  if [[ "$KEEP_ENV" =~ ^[Nn]$ ]]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo -e "${YELLOW}Please edit the .env file to update configurations:${NC}"
    echo -e "${YELLOW}  sudo nano $INSTALL_DIR/.env${NC}"
    read -p "Press Enter after you have updated the configuration..."
  fi
else
  # Check if .env.example exists
  if [ ! -f "$INSTALL_DIR/.env.example" ]; then
    echo -e "${YELLOW}Creating default .env file since .env.example doesn't exist${NC}"
    cat > "$INSTALL_DIR/.env" << EOF
# Database configuration
POSTGRES_USER=netmon
POSTGRES_PASSWORD=netmon_password
POSTGRES_DB=network_tests
POSTGRES_SCHEMA=network_eval

# Application configuration
SECRET_KEY=dev-key-change-in-production
FLASK_CONFIG=production

# Web server port
WEB_PORT=5000

# Network test configuration
TEST_TARGET=1.1.1.1
TEST_COUNT=400
TEST_INTERVAL=0.1
EOF
  else
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
  fi

  # Generate a secure random password and secret key
  RANDOM_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/")
  RANDOM_SECRET=$(openssl rand -hex 24)

  # Update the password and secret key in .env file
  sed -i "s/POSTGRES_PASSWORD=.*$/POSTGRES_PASSWORD=$RANDOM_PASSWORD/g" "$INSTALL_DIR/.env"
  sed -i "s/SECRET_KEY=.*$/SECRET_KEY=$RANDOM_SECRET/g" "$INSTALL_DIR/.env"

  echo -e "${YELLOW}Environment file created with secure random credentials.${NC}"
  echo -e "${YELLOW}Please review and edit if needed:${NC}"
  echo -e "${YELLOW}  sudo nano $INSTALL_DIR/.env${NC}"
  read -p "Press Enter after you have reviewed the configuration..."
fi

# Make sure the .env file has all required variables
if ! grep -q "POSTGRES_USER" "$INSTALL_DIR/.env"; then
  echo "POSTGRES_USER=netmon" >> "$INSTALL_DIR/.env"
fi
if ! grep -q "POSTGRES_DB" "$INSTALL_DIR/.env"; then
  echo "POSTGRES_DB=network_tests" >> "$INSTALL_DIR/.env"
fi
if ! grep -q "POSTGRES_SCHEMA" "$INSTALL_DIR/.env"; then
  echo "POSTGRES_SCHEMA=network_eval" >> "$INSTALL_DIR/.env"
fi

# Make the env file readable only by root
chmod 600 "$INSTALL_DIR/.env"
success "Environment variables configured"

# 4. Make scripts executable
chmod +x "$INSTALL_DIR/docker/init-db.sh"
chmod +x "$INSTALL_DIR/update.sh"
chmod +x "$INSTALL_DIR/uninstall.sh"
success "Scripts prepared"

# 5. Build and run Docker containers
progress "Building Docker containers..."
cd "$INSTALL_DIR"
docker compose build
success "Docker containers built successfully"

progress "Starting Docker containers..."
docker compose up -d
success "Docker containers started successfully"

# 6. Check if containers are running
progress "Checking container status..."
RUNNING_CONTAINERS=$(docker compose ps --services --filter "status=running" | wc -l)
# We expect at least 3 containers: db, web, test
# The db-init container will exit after successful completion
if [ "$RUNNING_CONTAINERS" -ge 3 ]; then
  success "All containers are running"
else
  echo -e "${RED}Some containers failed to start. Please check:${NC}"
  echo -e "${YELLOW}  cd $INSTALL_DIR && docker compose logs${NC}"
fi

# 7. Create bash shortcuts for easy update and uninstall
progress "Creating system-wide command shortcuts..."

# Create shortcut for update script
cat > /usr/local/bin/nes-update << EOF
#!/bin/bash
# Check if script is run with sudo
if [ \$EUID -ne 0 ]; then
  echo -e "\033[1;33mThis command requires root privileges. Running with sudo...\033[0m"
  exec sudo "\$0" "\$@"
  exit \$?
fi

# Ensure we're in the correct directory regardless of where the command is run from
cd $INSTALL_DIR
./update.sh
EOF
chmod +x /usr/local/bin/nes-update

# Create shortcut for uninstall script
cat > /usr/local/bin/nes-remove << EOF
#!/bin/bash
# Check if script is run with sudo
if [ \$EUID -ne 0 ]; then
  echo -e "\033[1;33mThis command requires root privileges. Running with sudo...\033[0m"
  exec sudo "\$0" "\$@"
  exit \$?
fi

# Ensure we're in the correct directory regardless of where the command is run from
cd $INSTALL_DIR
./uninstall.sh
EOF
chmod +x /usr/local/bin/nes-remove

success "Command shortcuts created: nes-update and nes-remove"

# 8. Provide final instructions
WEB_PORT=$(grep "WEB_PORT" "$INSTALL_DIR/.env" | cut -d '=' -f2 || echo "5000")
HOST_IP=$(hostname -I | awk '{print $1}')

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}    Installation completed successfully!    ${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "\nThe Network Evaluation Service has been installed and configured with Docker."
echo -e "You can access the web dashboard at: ${YELLOW}http://$HOST_IP:$WEB_PORT${NC}"
echo -e "\nImportant paths:"
echo -e "  - Installation directory: ${YELLOW}$INSTALL_DIR${NC}"
echo -e "  - Configuration: ${YELLOW}$INSTALL_DIR/.env${NC}"
echo -e "  - Docker Compose file: ${YELLOW}$INSTALL_DIR/docker-compose.yml${NC}"
echo -e "\nUseful commands:"
echo -e "  - View logs: ${YELLOW}cd $INSTALL_DIR && docker compose logs -f${NC}"
echo -e "  - Restart services: ${YELLOW}cd $INSTALL_DIR && docker compose restart${NC}"
echo -e "  - Update services: ${YELLOW}nes-update${NC} or ${YELLOW}$INSTALL_DIR/update.sh${NC}"
echo -e "  - Uninstall service: ${YELLOW}nes-remove${NC} or ${YELLOW}$INSTALL_DIR/uninstall.sh${NC}"
