# Network Evaluation Service

Is your ISP giving you the run-around with your intermittent drops? Are you having issues with your home network configuration? NES aims to give a minute by minute picture into your home network by collecting ping, jitter, and packet loss data on an ongoing basis.


https://github.com/user-attachments/assets/829a8f7a-474e-4344-8744-e8529229fbba


## Features

- Automated ping tests to measure network latency, jitter, and packet loss
- By default runs test run every minute, using 400 pings at a 0.1s interval. This is configurable in the .env.
- Web dashboard with real-time visualization and filtering for last 3 hours, 12 hours, 24 hours, 3 days, and 7 days.
- Results stored in PostgreSQL database and scalable for future feature development.
- Docker-based deployment to local host, Raspi, or Proxmox LXC

## Installation

### Quick Install with Docker

If you already have Docker and Docker Compose installed, you can get up and running with just a few commands:

```bash
# Navigate to the directory you wish to install the program in
cd /opt

# Clone the repository
git clone https://github.com/hendemic/network-eval-service.git
cd network-eval-service

# Build and start containers
docker compose build
docker compose up -d
```

The web interface will be available at `http://localhost:5000`

Environment variables can be customized by creating a `.env` file in the project directory with any of these values:
- `POSTGRES_USER`: Database username (default: netmon)
- `POSTGRES_PASSWORD`: Database password (default: netmon)
- `POSTGRES_DB`: Database name (default: network_tests)
- `POSTGRES_SCHEMA`: Schema name (default: network_eval)
- `WEB_PORT`: Web interface port (default: 5000)
- `TEST_TARGET`: IP to ping (default: 1.1.1.1)
- `TEST_COUNT`: Number of pings per test (default: 400)
- `PING_INTERVAL`: Seconds between pings (default: 0.1)
- `TEST_INTERVAL`: Seconds between tests (default: 60)

### Installer Script

For systems without Docker or for easier installation, an installer script is provided. You can still use this if you have Docker and Docker Compose, as the script will check for those dependencies and continue if you already have them.

#### Prerequisites
- Any debian based system
- Internet access for downloading dependencies and container images

#### Proxmox LXC Installation Considerations
It is recommended that you use a Debian 12 LXC if installing on Proxmox. Set up your new container, and then make sure required packages are installed.

```bash
apt update && apt install git curl sudo
```

> **Caution**: **The install.sh script is not a Proxmox Helper Script.** Do not run the install script on your host in Proxmox. If you are using Proxmox, this is meant to be run in an LXC container you create for NES or intend to run NES in alongside other Docker apps.

#### Install Process
Navigate to the directory you prefer to clone source to for install. If you're unsure, /usr/local/src is a common convention and will work for this install.
```bash
cd /usr/local/src/
```

Clone the repository, and run the install script
```bash
# Clone the repository
sudo git clone https://github.com/hendemic/network-eval-service.git
cd network-eval-service

# Make the install script executable
sudo chmod +x install.sh

# Run the installer
sudo ./install.sh
```

The installer will:
1. Install Docker and Docker Compose if they are not already installed
2. Clone the repository (or update it if it already exists)
3. Configure environment variables
4. Build and start Docker containers
5. Create Bash shortcuts for the update and uninstall scripts.

The installer will prompt you to choose between production (stable) or development (latest) branches. Unless you are contributing to the project, its highly recommended that you use production and not the development branch if you are an end user.

## Usage
Access the web dashboard at: `http://YOUR_SERVER_IP:5000`

> **Note**: if you've configured a different port, replace 5000 with the port you've configured for the web interface.

## Configuration
Configuration is done through environment variables in the `.env` file located in /opt/network-evaluation-service. Important settings include:

- `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database credentials
- `WEB_PORT` - The port to expose the web interface (default: 5000)
- `TEST_TARGET` - IP address or hostname to ping (default: 1.1.1.1)
- `TEST_COUNT` - Number of pings per test (default: 400)
- `PING_INTERVAL` - Interval between individual pings in seconds (default: 0.1)
- `TEST_INTERVAL` - Interval between tests in seconds (default: 60)

## Upgrading
There is an update utility provided, which can be found in your program files (`/opt/network-evaluation-service/update.sh` by default). If you installed with the install script, it set up a bash short cut (`nes-update`) for convenience.

For the easiest update use the following command (the current working directory is not relevant):
```bash
nes-update
```

If you wish to update manually you can do the following:
```bash
# Go to the project directory
cd /opt/network-evaluation-service  # or wherever you installed it if you installed without the install script.

# Stop docker containers
docker compose down

# Pull the latest changes
git pull

# Rebuild and restart containers
docker compose build
docker compose up
```

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

## Removal
To remove the program
- remove the directory /opt/network-evaluation-service/
- remove the docker containers and volumes
- remove bash shortcuts for nes-remove and nes-update

There is a script available to simplify uninstallation.
```bash
nes-remove
```
> **Warning**: This is experimental, and removes directories and docker containers + volumes with root access. It has been tested on a Proxmox LXC and a Raspi with no issues. However, if you are not comfortable please manually remove instead.

## Development
### Branch Structure
This project follows git flow conventions with new features currently under active development branched by `feature/*`, releases staged in `release/*`, and urgent bugs under development in `hotfixes/*`.

Additionally
- `main`: this is the development branch with the most recent stable development build.
- `production`: this is the stable branch for named releases for use by end users.

### Project Structure
- `/backend`: Python Flask backend API and test scripts
- `/frontend`: Vue.js frontend application with D3.js visualizations
- `/docker`: Docker configuration files

## Docker Containers
The application runs in three Docker containers:
1. **Web Container** - Flask backend with Vue.js frontend
2. **Test Container** - Runs ping tests on a schedule using cron
3. **Database Container** - PostgreSQL database to store test results


## License
[MIT License](LICENSE)
