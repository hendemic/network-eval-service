# Network Evaluation Service

A complete monitoring solution that runs network tests in a Debian LXC environment, stores results in a PostgreSQL database, and visualizes performance metrics over time using Vue.js and D3.js.

## Features

- Automated ping tests to measure network latency, jitter, and packet loss
- Tests run every minute using systemd timers
- Results stored in PostgreSQL database
- Web dashboard with real-time visualization using Vue.js and D3.js
- Historical data analysis with flexible time ranges

## Project Structure

- `/backend`: Python Flask backend API and test scripts
- `/frontend`: Vue.js frontend application with D3.js visualizations
- `/systemd`: Service and timer definitions for scheduled execution

## Prerequisites

- Debian-based LXC container
- Python 3.8+ with pip
- Node.js 16+ and npm
- PostgreSQL 12+

## Installation Options

### Automated Installation (Recommended)

The project includes an automated installation script that will set up everything in your LXC container:

```bash
# Clone the repository
git clone https://github.com/hendemic/network-eval-service.git
cd network-eval-service

# Make the install script executable
chmod +x install.sh

# Run the installer
sudo ./install.sh
```

### Proxmox LXC Installation

1. **Create a Debian LXC Container in Proxmox**:
   - From the Proxmox web interface, create a new LXC container
   - Use Debian 11 (Bullseye) or newer
   - Allocate at least 1GB RAM and 2 CPU cores
   - Set network configuration as needed (DHCP or static IP)
   - Start the container after creation

2. **Install Using the Script**:
   - Connect to your container: `pct enter CONTAINER_ID`
   - Install git: `apt update && apt install -y git`
   - Clone the repository: `git clone https://github.com/hendemic/network-eval-service.git`
   - Run the installer:
     ```bash
     cd network-eval-service
     chmod +x install.sh
     ./install.sh
     ```

3. **Access the Dashboard**:
   - The web interface will be available at `http://CONTAINER_IP:5000`
   - If needed, set up port forwarding in Proxmox to expose the service

### Manual Installation

For detailed step-by-step manual installation, follow these steps:

#### 1. Database Setup

```bash
# Install PostgreSQL if not already installed
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
postgres=# CREATE DATABASE network_tests;
postgres=# CREATE USER netmon WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE network_tests TO netmon;
postgres=# \q

# Set environment variables for database connection
export POSTGRES_USER=netmon
export POSTGRES_PASSWORD=your_password
export POSTGRES_DB=network_tests
```

#### 2. Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/network-evaluation-service.git
cd network-evaluation-service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python backend/db_init.py

# Test the ping script
python backend/pingTest.py
```

#### 3. Frontend Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Build for production
npm run build
```

#### 4. Systemd Service Setup

```bash
# Copy service files to systemd
sudo cp systemd/* /etc/systemd/system/

# Make the run_test.py script executable
chmod +x backend/run_test.py

# Reload systemd configurations
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable network-test.timer
sudo systemctl start network-test.timer
sudo systemctl enable network-web.service
sudo systemctl start network-web.service
```

## Upgrading

To upgrade to a newer version:

```bash
# Go to the project directory
cd /opt/network-evaluation-service  # or wherever you installed it

# Pull the latest changes
git pull

# Rebuild the frontend
cd frontend
npm install
npm run build

# Restart services
sudo systemctl restart network-web.service
sudo systemctl restart network-test.timer
```

## Usage

Access the web dashboard at: `http://CONTAINER_IP:5000`

## Development

### Backend Development

```bash
# Start Flask development server
export FLASK_APP=backend.app
export FLASK_ENV=development
flask run
```

### Frontend Development

```bash
# Start Vue development server with hot-reload
cd frontend
npm run serve
```

## Troubleshooting

If you encounter issues:

1. Check service status:
   ```bash
   systemctl status network-web.service
   systemctl status network-test.service
   ```

2. View application logs:
   ```bash
   journalctl -u network-web.service
   journalctl -u network-test.service
   ```

3. Test database connectivity:
   ```bash
   cd /opt/network-evaluation-service
   source venv/bin/activate
   python -c "from backend.models import db, PingResult; from backend.app import create_app; app = create_app(); app.app_context().push(); print(PingResult.query.count())"
   ```

## License

[MIT License](LICENSE)
