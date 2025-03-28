import os
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.models import db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Setup logging manually if fileConfig can't be used
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
    logger.info("Alembic config file not found or does not contain formatting configuration. Using default logging setup.")

# add your model's MetaData object here
from backend.models import metadata as target_metadata
# target_metadata = mymodel.Base.metadata
# target_metadata is already imported from models

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_engine_url():
    """Get the database URL from environment variables or config."""
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "network_tests")
    schema = os.getenv("POSTGRES_SCHEMA", "network_eval")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Set schema name for migrations
    config.set_main_option('sqlalchemy.schema', os.environ.get('POSTGRES_SCHEMA', 'network_eval'))
    config.set_main_option('sqlalchemy.url', get_engine_url())
    
    context.configure(
        url=config.get_main_option('sqlalchemy.url'),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema=config.get_main_option('sqlalchemy.schema')
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Set schema name for migrations
    config.set_main_option('sqlalchemy.schema', os.environ.get('POSTGRES_SCHEMA', 'network_eval'))
    config.set_main_option('sqlalchemy.url', get_engine_url())
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema=config.get_main_option('sqlalchemy.schema')
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()