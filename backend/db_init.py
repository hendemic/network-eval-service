from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
import os
import subprocess

from models import db
from config import config

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
        
        # Initialize migrations if needed
        if not os.path.exists('migrations'):
            print("Initializing migrations directory...")
            init()
            
            # Update the migrations/env.py to use the custom schema
            if os.path.exists('migrations/env.py'):
                with open('migrations/env.py', 'r') as f:
                    env_content = f.read()
                
                # Update the env.py file to include schema_name in render_item
                updated_env_content = env_content.replace(
                    "# add your model's MetaData object here",
                    "# add your model's MetaData object here\nfrom models import metadata as target_metadata"
                ).replace(
                    "config.set_main_option(",
                    "# Set schema name for migrations\nconfig.set_main_option('sqlalchemy.schema', os.environ.get('POSTGRES_SCHEMA', 'network_eval'))\n    config.set_main_option("
                ).replace(
                    "target_metadata = mymodel.Base.metadata",
                    "# target_metadata = mymodel.Base.metadata\n# target_metadata is already imported from models"
                ).replace(
                    "import os",
                    "import os\nfrom models import db"
                )
                
                with open('migrations/env.py', 'w') as f:
                    f.write(updated_env_content)
                
                print("Updated migrations/env.py with schema configuration.")
        
        # Create initial migration
        print("Creating migration...")
        migrate()
        
        # Apply migration
        print("Applying migration...")
        upgrade()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()