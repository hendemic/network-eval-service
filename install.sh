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

# Default verbosity level (0 = compact, 1 = verbose)
VERBOSE=0

# Parse command line arguments
usage() {
  echo "Usage: $0 [-v|--verbose] [-h|--help]"
  echo "  -v, --verbose   Display detailed installation information"
  echo "  -h, --help      Display this help message"
  exit 1
}

# Parse command-line options
while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Print header
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Network Evaluation Service Installer     ${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "Running in $([ $VERBOSE -eq 1 ] && echo 'verbose' || echo 'compact') mode. Use -v for detailed output."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run this script as root or with sudo${NC}"
  exit 1
fi

# Function to display progress (always shown)
progress() {
  echo -e "${YELLOW}➤ $1${NC}"
}

# Function to display success (always shown)
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to display debug information (only in verbose mode)
debug() {
  if [ $VERBOSE -eq 1 ]; then
    echo -e "  $1"
  fi
}

# Function to execute commands with appropriate verbosity
run_cmd() {
  if [ $VERBOSE -eq 1 ]; then
    "$@"
  else
    "$@" > /dev/null
  fi
}

# Function to check for required tools
check_requirements() {
  progress "Checking requirements..."

  # Check both Docker and Docker Compose upfront
  debug "Checking for Docker installation..."
  HAS_DOCKER=0
  HAS_COMPOSE=0
  MISSING_TOOLS=""
  
  if command -v docker &> /dev/null; then
    debug "Docker is already installed."
    HAS_DOCKER=1
  else
    MISSING_TOOLS="Docker"
  fi
  
  debug "Checking for Docker Compose installation..."
  if command -v docker compose &> /dev/null; then
    debug "Docker Compose is already installed."
    HAS_COMPOSE=1
  else
    if [ -z "$MISSING_TOOLS" ]; then
      MISSING_TOOLS="Docker Compose"
    else
      MISSING_TOOLS="Docker and Docker Compose"
    fi
  fi
  
  # If any tools are missing, prompt for installation
  if [ -n "$MISSING_TOOLS" ]; then
    echo -e "${YELLOW}$MISSING_TOOLS not found on this system.${NC}"
    echo -e "$MISSING_TOOLS required to run Network Evaluation Service."
    read -p "Would you like to install $MISSING_TOOLS now? (Y/n): " INSTALL_MISSING
    
    if [[ ! "$INSTALL_MISSING" =~ ^[Nn]$ ]]; then
      # Install Docker if needed
      if [ $HAS_DOCKER -eq 0 ]; then
        echo -e "Installing Docker (this may take a few minutes)..."
        if [ $VERBOSE -eq 1 ]; then
          curl -fsSL https://get.docker.com -o get-docker.sh
          sh get-docker.sh
        else
          echo -n "  Progress: "
          # Download and run Docker install script in background
          curl -fsSL https://get.docker.com -o get-docker.sh > /dev/null 2>&1
          sh get-docker.sh > /dev/null 2>&1 &
          docker_install_pid=$!
          
          # Display progress indicator
          spinner=( "|" "/" "-" "\\" )
          i=0
          while kill -0 $docker_install_pid 2>/dev/null; do
            echo -ne "\b${spinner[$i]}"
            i=$(( (i+1) % 4 ))
            sleep 1
          done
          
          # Check installation success
          wait $docker_install_pid
          if [ $? -eq 0 ]; then
            echo -e "\b ${GREEN}Done!${NC}"
          else
            echo -e "\b ${RED}Failed!${NC}"
            echo -e "${RED}Docker installation failed. Please install Docker manually before continuing.${NC}"
            exit 1
          fi
        fi
        rm get-docker.sh
        echo -e "${GREEN}Docker has been successfully installed.${NC}"
      fi
      
      # Install Docker Compose if needed
      if [ $HAS_COMPOSE -eq 0 ]; then
        echo -e "Installing Docker Compose plugin..."
        if [ $VERBOSE -eq 1 ]; then
          apt-get update
          apt-get install -y docker-compose-plugin
        else
          echo -n "  Progress: "
          # Install Docker Compose in background
          {
            apt-get update > /dev/null 2>&1
            apt-get install -y docker-compose-plugin > /dev/null 2>&1
          } &
          compose_install_pid=$!
          
          # Display progress indicator
          spinner=( "|" "/" "-" "\\" )
          i=0
          while kill -0 $compose_install_pid 2>/dev/null; do
            echo -ne "\b${spinner[$i]}"
            i=$(( (i+1) % 4 ))
            sleep 1
          done
          
          # Check installation success
          wait $compose_install_pid
          if [ $? -eq 0 ]; then
            echo -e "\b ${GREEN}Done!${NC}"
          else
            echo -e "\b ${RED}Failed!${NC}"
            echo -e "${RED}Docker Compose installation failed. Please install Docker Compose manually before continuing.${NC}"
            exit 1
          fi
        fi
        echo -e "${GREEN}Docker Compose has been successfully installed.${NC}"
      fi
    else
      echo -e "${RED}$MISSING_TOOLS required but will not be installed.${NC}"
      echo -e "Please install $MISSING_TOOLS first and then run this installer again."
      exit 1
    fi
  fi

  # Verify docker is running
  debug "Verifying Docker service is running..."
  if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Docker is not running. Starting Docker...${NC}"
    systemctl start docker
    if [ $? -ne 0 ]; then
      echo -e "${RED}Failed to start Docker service. Please start Docker manually before continuing.${NC}"
      exit 1
    fi
    echo -e "${GREEN}Docker service started successfully.${NC}"
  else
    debug "Docker service is running."
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
  debug "Fetching latest updates..."
  if [ $VERBOSE -eq 1 ]; then
    git fetch
    git checkout $GIT_BRANCH
    git pull origin $GIT_BRANCH
  else
    git fetch > /dev/null 2>&1
    git checkout $GIT_BRANCH > /dev/null 2>&1
    git pull origin $GIT_BRANCH > /dev/null 2>&1
  fi
else
  debug "Cloning repository to $INSTALL_DIR..."
  if [ $VERBOSE -eq 1 ]; then
    git clone -b $GIT_BRANCH $REPO_URL "$INSTALL_DIR"
  else
    git clone -b $GIT_BRANCH $REPO_URL "$INSTALL_DIR" > /dev/null 2>&1
  fi
  cd "$INSTALL_DIR"
fi
success "Repository cloned successfully ($BRANCH_NAME branch)"

# 3. Configure environment variables
progress "Configuring environment variables..."
if [ -f "$INSTALL_DIR/.env" ]; then
  echo -e "${YELLOW}Environment file already exists.${NC}"
  read -p "Do you want to keep the existing configuration? (Y/n): " KEEP_ENV
  if [[ "$KEEP_ENV" =~ ^[Nn]$ ]]; then
    debug "Copying example environment file..."
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo -e "${YELLOW}Default configuration has been created at:${NC} ${INSTALL_DIR}/.env"
    echo -e "${YELLOW}You can edit the UI port, test parameters, and other variables in this file.${NC}"
    read -p "Press Enter to continue..."
  else
    debug "Keeping existing environment configuration."
  fi
else
  # Check if .env.example exists
  if [ ! -f "$INSTALL_DIR/.env.example" ]; then
    debug "No example environment file found. Creating default configuration..."
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
    debug "Copying example environment file..."
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
  fi

  # Generate a secure random password and secret key
  debug "Generating secure random credentials..."
  RANDOM_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/")
  RANDOM_SECRET=$(openssl rand -hex 24)

  # Update the password and secret key in .env file
  debug "Updating credentials in environment file..."
  sed -i "s/POSTGRES_PASSWORD=.*$/POSTGRES_PASSWORD=$RANDOM_PASSWORD/g" "$INSTALL_DIR/.env"
  sed -i "s/SECRET_KEY=.*$/SECRET_KEY=$RANDOM_SECRET/g" "$INSTALL_DIR/.env"

  echo -e "${YELLOW}Default configuration has been created at:${NC} ${INSTALL_DIR}/.env"
  echo -e "${YELLOW}You can edit the UI port, test parameters, and other variables in this file.${NC}"
  read -p "Press Enter to continue..."
fi

# Make sure the .env file has all required variables
debug "Verifying required environment variables..."
if ! grep -q "POSTGRES_USER" "$INSTALL_DIR/.env"; then
  debug "Adding missing POSTGRES_USER variable..."
  echo "POSTGRES_USER=netmon" >> "$INSTALL_DIR/.env"
fi
if ! grep -q "POSTGRES_DB" "$INSTALL_DIR/.env"; then
  debug "Adding missing POSTGRES_DB variable..."
  echo "POSTGRES_DB=network_tests" >> "$INSTALL_DIR/.env"
fi
if ! grep -q "POSTGRES_SCHEMA" "$INSTALL_DIR/.env"; then
  debug "Adding missing POSTGRES_SCHEMA variable..."
  echo "POSTGRES_SCHEMA=network_eval" >> "$INSTALL_DIR/.env"
fi

# Make the env file readable only by root
debug "Setting secure permissions on environment file..."
chmod 600 "$INSTALL_DIR/.env"
success "Environment variables configured"

# 4. Make scripts executable
debug "Setting executable permissions on scripts..."
chmod +x "$INSTALL_DIR/docker/init-db.sh"
chmod +x "$INSTALL_DIR/update.sh"
chmod +x "$INSTALL_DIR/uninstall.sh"
success "Scripts prepared"

# 5. Build and run Docker containers
progress "Building Docker containers..."
cd "$INSTALL_DIR"

# Ensure the VERSION file is copied to the frontend static files
if [ -f "$INSTALL_DIR/VERSION" ]; then
  debug "Copying VERSION file to frontend..."
  mkdir -p "$INSTALL_DIR/frontend/public"
  cp "$INSTALL_DIR/VERSION" "$INSTALL_DIR/frontend/public/"
  success "VERSION file copied to frontend"
fi

echo -e "${YELLOW}Building Docker containers (this may take several minutes)...${NC}"
if [ $VERBOSE -eq 1 ]; then
  # In verbose mode, show full build output
  docker compose build
else
  # In compact mode, show progress indicators
  echo -n "  Progress: "
  # Run docker compose build in background and capture its PID
  docker compose build > /dev/null 2>&1 &
  build_pid=$!
  
  # Display progress indicator while build is running
  spinner=( "|" "/" "-" "\\" )
  i=0
  while kill -0 $build_pid 2>/dev/null; do
    echo -ne "\b${spinner[$i]}"
    i=$(( (i+1) % 4 ))
    sleep 1
  done
  
  # Check if build completed successfully
  wait $build_pid
  if [ $? -ne 0 ]; then
    echo -e "\b ${RED}Failed!${NC}"
    echo -e "${RED}Docker build failed. Run with -v for detailed output.${NC}"
    exit 1
  else
    echo -e "\b ${GREEN}Done!${NC}"
  fi
fi
success "Docker containers built successfully"

progress "Starting Docker containers..."
debug "Starting services with docker compose..."
if [ $VERBOSE -eq 1 ]; then
  docker compose up -d
else
  echo -n "  Progress: "
  # Run docker compose up in background
  docker compose up -d > /dev/null 2>&1 &
  startup_pid=$!
  
  # Display progress indicator while startup is running
  spinner=( "|" "/" "-" "\\" )
  i=0
  while kill -0 $startup_pid 2>/dev/null; do
    echo -ne "\b${spinner[$i]}"
    i=$(( (i+1) % 4 ))
    sleep 0.5  # Faster spinner as this usually takes less time
  done
  
  # Check if startup completed successfully
  wait $startup_pid
  if [ $? -ne 0 ]; then
    echo -e "\b ${RED}Failed!${NC}"
    echo -e "${RED}Docker startup failed. Run with -v for detailed output.${NC}"
    exit 1
  else
    echo -e "\b ${GREEN}Done!${NC}"
  fi
fi
success "Docker containers started successfully"

# 6. Check if containers are running
progress "Checking container status..."
debug "Counting running containers..."
RUNNING_CONTAINERS=$(docker compose ps --services --filter "status=running" | wc -l)
# We expect at least 3 containers: db, web, test
# The db-init container will exit after successful completion
if [ "$RUNNING_CONTAINERS" -ge 3 ]; then
  success "All containers are running"
  if [ $VERBOSE -eq 1 ]; then
    echo "Running containers:"
    docker compose ps
  fi
else
  echo -e "${RED}Some containers failed to start. Please check:${NC}"
  echo -e "${YELLOW}  cd $INSTALL_DIR && docker compose logs${NC}"
  if [ $VERBOSE -eq 1 ]; then
    echo "Container status:"
    docker compose ps
    echo "Last 20 log lines:"
    docker compose logs --tail=20
  fi
fi

# 7. Create bash shortcuts for easy update and uninstall
progress "Creating system-wide command shortcuts..."
debug "Creating nes-update command..."

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
./update.sh \$@
EOF
chmod +x /usr/local/bin/nes-update

# Create a completely self-contained uninstall script that doesn't depend on files in the installation dir
debug "Creating nes-remove command..."
cat > /usr/local/bin/nes-remove << 'EOF'
#!/bin/bash
# Network Evaluation Service - Uninstall Script

# Default verbosity level (0 = compact, 1 = verbose)
VERBOSE=0

# Parse command line arguments
usage() {
  echo "Usage: $0 [-v|--verbose] [-h|--help]"
  echo "  -v, --verbose   Display detailed uninstallation information"
  echo "  -h, --help      Display this help message"
  exit 1
}

# Parse command-line options
while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Check if script is run with sudo
if [ $EUID -ne 0 ]; then
  echo -e "\033[1;33mThis command requires root privileges. Running with sudo...\033[0m"
  exec sudo "$0" "$@"
  exit $?
fi

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
echo -e "Running in \$([ \$VERBOSE -eq 1 ] && echo 'verbose' || echo 'compact') mode. Use -v for detailed output."

# Function to display progress (always shown)
progress() {
  echo -e "${YELLOW}➤ $1${NC}"
}

# Function to display success (always shown)
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to display debug information (only in verbose mode)
debug() {
  if [ $VERBOSE -eq 1 ]; then
    echo -e "  $1"
  fi
}

# Function to execute commands with appropriate verbosity
run_cmd() {
  if [ $VERBOSE -eq 1 ]; then
    "$@"
  else
    "$@" > /dev/null
  fi
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

# Save docker-compose.yml path before we enter the directory
COMPOSE_FILE="$INSTALL_DIR/docker-compose.yml"

# Stop and remove containers, networks, and volumes
if [ -f "$COMPOSE_FILE" ]; then
  progress "Stopping and removing Docker containers, networks, and volumes..."

  # We use pushd/popd to safely change directory while keeping track of where we were
  pushd "$INSTALL_DIR" > /dev/null

  # The -v flag removes volumes defined in the compose file
  docker compose down -v

  # Get the directory name for container prefix (used by docker-compose)
  DIR_NAME=$(basename "$INSTALL_DIR")

  # Return to original directory immediately after docker compose command
  popd > /dev/null

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

# Don't remove ourselves yet - save that for last
NES_REMOVE_PATH="/usr/local/bin/nes-remove"

# Remove the installation directory
progress "Removing installation directory..."
echo "Attempting to remove directory: $INSTALL_DIR"

# First try with regular rm
if ! rm -rf "$INSTALL_DIR" 2>/dev/null; then
  echo "Standard removal failed, trying with additional permissions..."

  # Try to fix permissions and retry
  find "$INSTALL_DIR" -type d -exec chmod 755 {} \; 2>/dev/null
  find "$INSTALL_DIR" -type f -exec chmod 644 {} \; 2>/dev/null

  # Try again with removal
  if ! rm -rf "$INSTALL_DIR" 2>/dev/null; then
    echo "Using more forceful removal methods..."
    # Last resort: use a more forceful command combination
    find "$INSTALL_DIR" -delete 2>/dev/null
    rm -rf "$INSTALL_DIR" 2>/dev/null
  fi
fi

# Verify removal
if [ -d "$INSTALL_DIR" ]; then
  echo -e "${RED}Warning: Could not completely remove $INSTALL_DIR${NC}"
  echo -e "${YELLOW}You may need to manually remove it with: sudo rm -rf $INSTALL_DIR${NC}"
else
  success "Installation directory removed"
fi

# Now remove ourselves as the very last step
if [ -f "$NES_REMOVE_PATH" ]; then
  rm -f "$NES_REMOVE_PATH"
  echo "Removed nes-remove command"
fi
success "Command shortcuts removed"

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}    Uninstallation completed successfully!  ${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "\nNetwork Evaluation Service has been completely removed from your system."
EOF
chmod +x /usr/local/bin/nes-remove

success "Command shortcuts created: nes-update and nes-remove"

# 8. Provide final instructions
debug "Gathering configuration information for final message..."
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
echo -e "  - Update services: ${YELLOW}nes-update${NC} or ${YELLOW}$INSTALL_DIR/update.sh -v${NC}"
echo -e "  - Uninstall service: ${YELLOW}nes-remove${NC} or ${YELLOW}$INSTALL_DIR/uninstall.sh -v${NC}"
echo -e "    - ${RED}WARNING: The uninstall utility is experimental.${NC}"
echo -e "  - Add -v flag for verbose output: ${YELLOW}nes-update -v${NC} or ${YELLOW}nes-remove -v${NC}"
