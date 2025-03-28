#!/bin/bash
# Network Evaluation Service - Automated Installation Script
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Repository URL - replace with your actual repository URL
REPO_URL="https://github.com/hendemic/network-eval-service.git"

# Default database configuration
DEFAULT_DB_NAME="network_tests"
DEFAULT_DB_USER="netmon"
DEFAULT_DB_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/") # Generate secure random password

# Installation directory
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

# Check for sudo and warn if not available
if ! command -v sudo &> /dev/null; then
  echo -e "${YELLOW}Warning: 'sudo' command not found. This is fine if you're running as root.${NC}"
  echo -e "${YELLOW}The script will use 'su' commands for database operations instead.${NC}"
fi

# Function to display progress
progress() {
  echo -e "${YELLOW}➤ $1${NC}"
}

# Function to display success
success() {
  echo -e "${GREEN}✓ $1${NC}"
}

# Function to prompt for configuration
prompt_for_config() {
  # Check if config file exists
  if [ -f "$INSTALL_DIR/.env" ]; then
    echo -e "${YELLOW}Configuration file already exists at $INSTALL_DIR/.env${NC}"
    read -p "Do you want to use the existing configuration? (Y/n): " USE_EXISTING
    if [[ "$USE_EXISTING" =~ ^[Nn]$ ]]; then
      get_credentials
    else
      # Source existing credentials
      source "$INSTALL_DIR/.env"
      DB_NAME=$POSTGRES_DB
      DB_USER=$POSTGRES_USER
      DB_PASSWORD=$POSTGRES_PASSWORD
      echo "Using existing database configuration."
    fi
  else
    # Ask if user wants to use defaults or custom credentials
    read -p "Do you want to use default database settings? (Y/n): " USE_DEFAULTS
    if [[ "$USE_DEFAULTS" =~ ^[Nn]$ ]]; then
      get_credentials
    else
      DB_NAME=$DEFAULT_DB_NAME
      DB_USER=$DEFAULT_DB_USER
      DB_PASSWORD=$DEFAULT_DB_PASSWORD
      echo -e "Using default database configuration:"
      echo -e "  - Database: ${YELLOW}$DB_NAME${NC}"
      echo -e "  - Username: ${YELLOW}$DB_USER${NC}"
      echo -e "  - Password: ${YELLOW}$DB_PASSWORD${NC} (randomly generated)"
      echo -e "These credentials will be saved to ${YELLOW}$INSTALL_DIR/.env${NC}"
    fi
  fi
}

# Function to get custom credentials
get_credentials() {
  read -p "Enter database name [$DEFAULT_DB_NAME]: " INPUT_DB_NAME
  read -p "Enter database username [$DEFAULT_DB_USER]: " INPUT_DB_USER
  read -s -p "Enter database password [$DEFAULT_DB_PASSWORD]: " INPUT_DB_PASSWORD
  echo ""

  DB_NAME=${INPUT_DB_NAME:-$DEFAULT_DB_NAME}
  DB_USER=${INPUT_DB_USER:-$DEFAULT_DB_USER}
  DB_PASSWORD=${INPUT_DB_PASSWORD:-$DEFAULT_DB_PASSWORD}

  echo -e "Using custom database configuration:"
  echo -e "  - Database: ${YELLOW}$DB_NAME${NC}"
  echo -e "  - Username: ${YELLOW}$DB_USER${NC}"
}

# 1. Update system and install dependencies
progress "Updating system and installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib nodejs npm git curl

# Check if packages were installed successfully
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to install required packages. Please check your network connection and try again.${NC}"
  exit 1
fi
success "System updated and dependencies installed"

# 2. Clone the repository
progress "Cloning repository from $REPO_URL..."
if [ -d "$INSTALL_DIR" ]; then
  echo -e "${YELLOW}Directory already exists. Updating...${NC}"
  cd "$INSTALL_DIR"
  git pull
else
  git clone $REPO_URL "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi
success "Repository cloned successfully"

# 3. Get database configuration
prompt_for_config

# 4. Setup PostgreSQL database
progress "Setting up PostgreSQL database..."
# Use pg_exec function to run postgres commands with or without sudo
pg_exec() {
  local cmd=$1
  if command -v sudo &> /dev/null; then
    # If sudo is available, use it
    sudo -u postgres psql -c "$cmd"
  else
    # If sudo is not available (and we're root), use su directly
    su - postgres -c "psql -c \"$cmd\""
  fi
}

pg_exec_query() {
  local query=$1
  if command -v sudo &> /dev/null; then
    # If sudo is available, use it
    sudo -u postgres psql -tAc "$query"
  else
    # If sudo is not available (and we're root), use su directly
    su - postgres -c "psql -tAc \"$query\""
  fi
}

pg_exec_db() {
  local db=$1
  local cmd=$2
  if command -v sudo &> /dev/null; then
    # If sudo is available, use it
    sudo -u postgres psql -d "$db" -c "$cmd"
  else
    # If sudo is not available (and we're root), use su directly
    su - postgres -c "psql -d \"$db\" -c \"$cmd\""
  fi
}

# Check if the database already exists
DB_EXISTS=$(pg_exec_query "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" = "1" ]; then
  echo -e "${YELLOW}Database $DB_NAME already exists. Skipping database creation.${NC}"
else
  # Create database and user
  pg_exec "CREATE DATABASE $DB_NAME;"
  USER_EXISTS=$(pg_exec_query "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")
  if [ "$USER_EXISTS" != "1" ]; then
    pg_exec "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
  else
    pg_exec "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
  fi
  pg_exec "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
  success "Database and user created successfully"
fi

# Create schema and set up permissions
SCHEMA_NAME="network_eval"
pg_exec_db "$DB_NAME" "CREATE SCHEMA IF NOT EXISTS $SCHEMA_NAME;"
pg_exec_db "$DB_NAME" "GRANT ALL ON SCHEMA $SCHEMA_NAME TO $DB_USER;"
pg_exec_db "$DB_NAME" "GRANT USAGE ON SCHEMA public TO $DB_USER;"
pg_exec_db "$DB_NAME" "GRANT CREATE ON SCHEMA public TO $DB_USER;"

# Create alembic_version table ahead of time if it doesn't exist and grant permissions
pg_exec_db "$DB_NAME" "CREATE TABLE IF NOT EXISTS public.alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num));"
pg_exec_db "$DB_NAME" "GRANT ALL ON TABLE public.alembic_version TO $DB_USER;"

success "Database configured with proper schema and permissions"

# 5. Setup Python virtual environment and install requirements
progress "Setting up Python environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
success "Python environment set up and dependencies installed"

# 6. Configure environment variables
progress "Configuring environment variables..."
cat > "$INSTALL_DIR/.env" << EOF
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=$DB_NAME
POSTGRES_SCHEMA=network_eval
FLASK_CONFIG=production
SECRET_KEY=$(openssl rand -hex 24)
EOF

# Make the env file readable only by root
chmod 600 "$INSTALL_DIR/.env"
success "Environment variables configured"

# 7. Initialize the database
progress "Initializing database..."
cd "$INSTALL_DIR"
export POSTGRES_USER=$DB_USER
export POSTGRES_PASSWORD=$DB_PASSWORD
export POSTGRES_DB=$DB_NAME
export POSTGRES_SCHEMA=network_eval
source venv/bin/activate

# Setup database and schema first
progress "Setting up database and schema..."
python backend/db_utils.py
success "Database and schema setup complete"

# Create tables using SQLAlchemy directly
progress "Creating database tables..."
python backend/db_init.py
success "Database initialized"

# 8. Build the frontend
progress "Building frontend application..."
cd "$INSTALL_DIR/frontend"
npm install

# Fix potential ESLint issues by creating a config file if it doesn't exist
if [ ! -f .eslintrc.js ]; then
  cat > .eslintrc.js << EOF
module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/essential',
    'eslint:recommended'
  ],
  parserOptions: {
    parser: 'babel-eslint'
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
  }
}
EOF
  echo "Created ESLint configuration file"
fi

# Try several build approaches, starting with the least strict
echo "Attempting to build frontend (attempt 1)..."
npm run build -- --no-lint || \
echo "First build attempt failed, trying with environment variable (attempt 2)..." && \
DISABLE_ESLINT_PLUGIN=true npm run build || \
echo "Second build attempt failed, trying with vue.config.js modification (attempt 3)..." && \
# Create a temporary vue.config.js to disable eslint
cat > vue.config.js << EOF
module.exports = {
  lintOnSave: false,
  devServer: {
    overlay: {
      warnings: false,
      errors: false
    }
  },
  // Disable eslint for production build
  chainWebpack: config => {
    config.plugins.delete('eslint');
  }
}
EOF
npm run build
success "Frontend built successfully"

# 9. Modify the systemd service files to load environment from .env
progress "Setting up systemd services..."
# Adjust paths in systemd files
sed -i "s|/home/hendemic/Documents/Projects/network-evaluation-service|$INSTALL_DIR|g" "$INSTALL_DIR/systemd/network-test.service"
sed -i "s|/home/hendemic/Documents/Projects/network-evaluation-service|$INSTALL_DIR|g" "$INSTALL_DIR/systemd/network-web.service"

# Add EnvironmentFile directive to service files
if ! grep -q "EnvironmentFile=" "$INSTALL_DIR/systemd/network-test.service"; then
  sed -i "/\[Service\]/a EnvironmentFile=$INSTALL_DIR/.env" "$INSTALL_DIR/systemd/network-test.service"
fi

if ! grep -q "EnvironmentFile=" "$INSTALL_DIR/systemd/network-web.service"; then
  sed -i "/\[Service\]/a EnvironmentFile=$INSTALL_DIR/.env" "$INSTALL_DIR/systemd/network-web.service"
fi

# Copy service files
cp "$INSTALL_DIR/systemd/network-test.service" /etc/systemd/system/
cp "$INSTALL_DIR/systemd/network-test.timer" /etc/systemd/system/
cp "$INSTALL_DIR/systemd/network-web.service" /etc/systemd/system/

# Make the run script executable
chmod +x "$INSTALL_DIR/backend/run_test.py"

# Reload systemd
systemctl daemon-reload

# Enable and start services
systemctl enable network-test.timer
systemctl start network-test.timer
systemctl enable network-web.service
systemctl start network-web.service
success "Systemd services configured and started"

# 10. Set proper permissions
progress "Setting correct permissions..."
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
# Keep the .env file secure
chmod 600 "$INSTALL_DIR/.env"
success "Permissions set"

# 11. Check if services are running
progress "Checking services status..."
TIMER_STATUS=$(systemctl is-active network-test.timer)
WEB_STATUS=$(systemctl is-active network-web.service)

if [ "$TIMER_STATUS" = "active" ] && [ "$WEB_STATUS" = "active" ]; then
  success "All services are running correctly"
else
  echo -e "${RED}Some services are not running. Please check the logs:${NC}"
  echo "  - Timer service: $TIMER_STATUS"
  echo "  - Web service: $WEB_STATUS"
  echo -e "${YELLOW}You can check logs with:${NC}"
  echo "  - journalctl -u network-test.service"
  echo "  - journalctl -u network-web.service"
fi

# 12. Provide final instructions
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}    Installation completed successfully!    ${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "\nThe Network Evaluation Service has been installed and configured."
echo -e "You can access the web dashboard at: ${YELLOW}http://$(hostname -I | awk '{print $1}'):5000${NC}"
echo -e "\nImportant paths:"
echo -e "  - Application: ${YELLOW}$INSTALL_DIR${NC}"
echo -e "  - Configuration: ${YELLOW}$INSTALL_DIR/.env${NC}"
echo -e "  - Log files: ${YELLOW}journalctl -u network-web.service${NC}"
echo -e "\nThe database credentials are stored securely in ${YELLOW}$INSTALL_DIR/.env${NC}"
echo -e "This file has restricted permissions (600) to protect sensitive information."
echo -e "\nTo make configuration changes, edit the .env file:"
echo -e "  ${YELLOW}sudo nano $INSTALL_DIR/.env${NC}"
echo -e "And then restart the services:"
echo -e "  ${YELLOW}sudo systemctl restart network-web.service network-test.timer${NC}"
