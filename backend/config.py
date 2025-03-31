import os

class Config:
    # PostgreSQL database configuration
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'network_tests')
    POSTGRES_SCHEMA = os.environ.get('POSTGRES_SCHEMA', 'network_eval')
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Apply the schema when using models
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": f"-csearch_path={POSTGRES_SCHEMA}"}
    }
    
    # App configuration
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Network test configuration
    TEST_TARGET = os.environ.get('TEST_TARGET', '1.1.1.1')
    TEST_COUNT = int(os.environ.get('TEST_COUNT', '400'))
    TEST_INTERVAL = os.environ.get('TEST_INTERVAL', '60')  # Time between test runs in seconds
    PING_INTERVAL = os.environ.get('PING_INTERVAL', '0.1') # Time between pings in seconds

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    # Use in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Remove schema-specific options for SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {}

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}