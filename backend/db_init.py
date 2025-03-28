from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
import os
import subprocess
import sys

# Add parent directory to path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db
from backend.config import config

def init_db():
    # Create a minimal Flask app
    app = Flask(__name__)
    app.config.from_object(config['default'])
    
    # Initialize extensions
    db.init_app(app)
    migrate_manager = Migrate(app, db)
    
    with app.app_context():
        # Create database if it doesn't exist
        try:
            # Check if the database exists
            subprocess.run([
                "psql", 
                "-h", app.config['POSTGRES_HOST'],
                "-U", app.config['POSTGRES_USER'],
                "-p", app.config['POSTGRES_PORT'],
                "-d", "postgres",
                "-c", f"SELECT 1 FROM pg_database WHERE datname = '{app.config['POSTGRES_DB']}'"
            ], check=True, capture_output=True, env={"PGPASSWORD": app.config['POSTGRES_PASSWORD']})
            
            print(f"Database '{app.config['POSTGRES_DB']}' already exists.")
        except subprocess.CalledProcessError:
            # Create the database
            subprocess.run([
                "psql",
                "-h", app.config['POSTGRES_HOST'],
                "-U", app.config['POSTGRES_USER'],
                "-p", app.config['POSTGRES_PORT'],
                "-d", "postgres",
                "-c", f"CREATE DATABASE {app.config['POSTGRES_DB']}"
            ], check=True, env={"PGPASSWORD": app.config['POSTGRES_PASSWORD']})
            
            print(f"Created database '{app.config['POSTGRES_DB']}'.")
        
        # Ensure user has necessary privileges in the database
        try:
            # Connect to the target database and grant privileges
            subprocess.run([
                "psql",
                "-h", app.config['POSTGRES_HOST'],
                "-U", app.config['POSTGRES_USER'],
                "-p", app.config['POSTGRES_PORT'],
                "-d", app.config['POSTGRES_DB'],
                "-c", "CREATE SCHEMA IF NOT EXISTS network_eval; GRANT ALL ON SCHEMA network_eval TO CURRENT_USER;"
            ], check=True, env={"PGPASSWORD": app.config['POSTGRES_PASSWORD']})
            
            print("Permissions verified and schema created if needed.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not set up schema permissions: {e}")
            print("You may need to manually grant database privileges to the user.")
        
        # Make sure migrations directory structure is valid
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        migrations_dir = os.path.join(project_root, 'migrations')
        versions_dir = os.path.join(migrations_dir, 'versions')
        alembic_ini_path = os.path.join(project_root, 'migrations', 'alembic.ini')
        
        # Create versions directory if it doesn't exist
        os.makedirs(versions_dir, exist_ok=True)
        
        # Create alembic.ini if it doesn't exist
        if not os.path.exists(alembic_ini_path):
            with open(alembic_ini_path, 'w') as f:
                f.write("""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# timezone to use when rendering the date
# within the migration file as well as the filename.
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; this defaults
# to migrations/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path
# version_locations = %(here)s/bar %(here)s/bat migrations/versions

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = driver://user:pass@localhost/dbname


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks=black
# black.type=console_scripts
# black.entrypoint=black
# black.options=-l 79

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S""")
            print("Created alembic.ini file")
        
        # If migrations/env.py exists, validate and update it
        migrations_env_path = os.path.join(migrations_dir, 'env.py')
        if os.path.exists(migrations_env_path):
            with open(migrations_env_path, 'r') as f:
                env_content = f.read()
            
            # Make sure required imports are there
            if 'from backend.models import db' not in env_content:
                env_content = env_content.replace(
                    "from alembic import context",
                    "from alembic import context\nfrom backend.models import db"
                )
            
            if 'from backend.models import metadata as target_metadata' not in env_content:
                env_content = env_content.replace(
                    "# add your model's MetaData object here",
                    "# add your model's MetaData object here\nfrom backend.models import metadata as target_metadata"
                )
            
            if 'set_main_option(\'sqlalchemy.schema\'' not in env_content:
                env_content = env_content.replace(
                    "def run_migrations_offline():",
                    "def run_migrations_offline():\n    # Set schema name for migrations\n    config.set_main_option('sqlalchemy.schema', os.environ.get('POSTGRES_SCHEMA', 'network_eval'))"
                )
                env_content = env_content.replace(
                    "def run_migrations_online():",
                    "def run_migrations_online():\n    # Set schema name for migrations\n    config.set_main_option('sqlalchemy.schema', os.environ.get('POSTGRES_SCHEMA', 'network_eval'))"
                )
            
            # Add logging safety checks
            if 'try:' not in env_content and 'fileConfig(config.config_file_name)' in env_content:
                env_content = env_content.replace(
                    "fileConfig(config.config_file_name)",
                    """import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-5.5s [%(name)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('alembic.env')

# Try to set up logging using the config file, but don't fail if it can't be done
try:
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)
except (KeyError, AttributeError):
    logger.info("Alembic config file not found or does not contain formatting configuration. Using default logging setup.")"""
                )
            
            with open(migrations_env_path, 'w') as f:
                f.write(env_content)
            
            print("Updated migrations/env.py with schema configuration.")
        else:
            # If env.py doesn't exist at all, we need to initialize the migrations directory
            # But don't error out if it already exists
            try:
                print("Initializing migrations directory...")
                init()
                
                # Now update the newly created env.py
                if os.path.exists(migrations_env_path):
                    with open(migrations_env_path, 'r') as f:
                        env_content = f.read()
                    
                    # Update env.py with our customizations
                    env_content = env_content.replace(
                        "from alembic import context",
                        "from alembic import context\nfrom backend.models import db"
                    ).replace(
                        "target_metadata = None",
                        "from backend.models import metadata as target_metadata"
                    ).replace(
                        "fileConfig(config.config_file_name)",
                        """import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-5.5s [%(name)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('alembic.env')

# Try to set up logging using the config file, but don't fail if it can't be done
try:
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)
except (KeyError, AttributeError):
    logger.info("Alembic config file not found or does not contain formatting configuration. Using default logging setup.")"""
                    )
                    
                    with open(migrations_env_path, 'w') as f:
                        f.write(env_content)
                        
                    print("Updated newly created migrations/env.py with schema configuration.")
            except Exception as e:
                # If initialization fails because directory already exists, that's fine
                # We'll just use what's there
                print(f"Note: {e}")
                print("Using existing migrations directory.")
        
        # Create initial migration
        print("Creating migration...")
        migrate()
        
        # Apply migration
        print("Applying migration...")
        upgrade()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()