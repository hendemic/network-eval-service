# Network Evaluation Service

A complete monitoring solution that runs network tests, stores results in a PostgreSQL database, and visualizes performance metrics over time using Vue.js and D3.js.

## Features

- Automated ping tests to measure network latency, jitter, and packet loss
- Tests run every minute
- Results stored in PostgreSQL database
- Web dashboard with real-time visualization using Vue.js and D3.js
- Historical data analysis with flexible time ranges
- Docker-based deployment for easy installation and management

## Project Structure

- `/backend`: Python Flask backend API and test scripts
- `/frontend`: Vue.js frontend application with D3.js visualizations
- `/docker`: Docker configuration files

## Prerequisites

- Any Linux system (Debian, Ubuntu, RHEL, or Proxmox LXC containers)
- Internet access for downloading dependencies and container images

The installer will automatically check for Docker and Docker Compose and install them if needed.

## Installation

```bash
# Clone the repository
git clone https://github.com/hendemic/network-eval-service.git
cd network-eval-service

# Make the install script executable
chmod +x install.sh

# Run the installer
sudo ./install.sh
```

The installer will:
1. Install Docker if it's not already installed
2. Clone the repository (or update it if it already exists)
3. Configure environment variables
4. Build and start Docker containers
5. Create a systemd service for automatic startup

The installer will prompt you to choose between production (stable) or development (latest) branches.

## Docker Containers

The application runs in three Docker containers:

1. **Web Container** - Flask backend with Vue.js frontend
2. **Test Container** - Runs ping tests on a schedule using cron
3. **Database Container** - PostgreSQL database to store test results

## Configuration

Configuration is done through environment variables in the `.env` file. Important settings include:

- `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database credentials
- `WEB_PORT` - The port to expose the web interface (default: 5000)
- `TEST_TARGET` - IP address or hostname to ping (default: 1.1.1.1)
- `TEST_COUNT` - Number of pings per test (default: 100)
- `TEST_INTERVAL` - Interval between pings in seconds (default: 0.1)

## Upgrading

To upgrade to a new version:

```bash
# Go to the project directory
cd /opt/network-evaluation-service  # or wherever you installed it

# Pull the latest changes
git pull

# Rebuild and restart containers
docker compose up -d --build
```

## Usage

Access the web dashboard at: `http://YOUR_SERVER_IP:5000`

The dashboard shows:
- Current network status
- Historical latency, jitter, and packet loss graphs
- 24-hour statistics

## Troubleshooting

If you encounter issues, you can use the included debug script:

```bash
cd /opt/network-evaluation-service
./docker-debug.sh
```

This script will:
- Show the status of all containers
- Display environment variables
- Show logs from all containers
- Test database connectivity
- Check for database tables

You can also troubleshoot manually:

1. Check container status:
   ```bash
   docker compose ps
   ```

2. View container logs:
   ```bash
   # View logs for all containers
   docker compose logs

   # View logs for a specific service
   docker compose logs web
   docker compose logs test
   docker compose logs db
   docker compose logs db-init
   ```

3. Check database initialization:
   ```bash
   # Connect to the PostgreSQL database
   docker compose exec db psql -U netmon -d network_tests

   # Inside PostgreSQL, check the schema and tables
   \dn  -- List schemas
   \dt network_eval.*  -- List tables in the network_eval schema
   ```

4. Restart Docker containers:
   ```bash
   docker compose down
   docker compose up -d
   ```

## License

[MIT License](LICENSE)
