from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.schema import MetaData
from backend.config import config

# Create a MetaData object without a schema initially
# This allows for flexibility with different database backends
metadata = MetaData()

# Initialize SQLAlchemy with the metadata configuration
# This creates the core database interface used throughout the application
db = SQLAlchemy(metadata=metadata)

def configure_schema_if_postgres(app):
    """Configure the PostgreSQL schema for database tables.
    
    This function should be called during application initialization
    to set the schema only when using PostgreSQL. For SQLite and other
    databases, schemas aren't used or are handled differently.
    
    Args:
        app: Flask application instance with configuration loaded
    """
    # Check if we're using PostgreSQL by examining the database URI
    if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        # Set the schema before any tables are created
        # This ensures all tables will be created in the specified schema
        db.metadata.schema = config['default'].POSTGRES_SCHEMA

class PingResult(db.Model):
    """Database model for storing network ping test results.
    
    This model represents the core data structure of the application,
    storing all network performance metrics collected by ping tests.
    """
    __tablename__ = 'ping_results'
    
    # Primary key and timestamp (indexed for efficient time-based queries)
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Network test parameters
    target = db.Column(db.String(50), nullable=False)  # IP address or hostname that was pinged
    
    # Core network metrics
    packet_loss = db.Column(db.Float, nullable=False)  # Percentage of packets lost (0-100)
    min_latency = db.Column(db.Float)  # Minimum round-trip time in milliseconds
    max_latency = db.Column(db.Float)  # Maximum round-trip time in milliseconds
    avg_latency = db.Column(db.Float)  # Average round-trip time in milliseconds
    jitter = db.Column(db.Float)  # Variation in latency (calculated from consecutive packets)
    
    # Test details
    packets_sent = db.Column(db.Integer, nullable=False)  # Total number of packets sent
    packets_received = db.Column(db.Integer, nullable=False)  # Total number of packets received
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization.
        
        Returns:
            Dictionary with all ping test results formatted for API responses
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),  # ISO format for consistent datetime handling
            'target': self.target,
            'packet_loss': self.packet_loss,
            'min_latency': self.min_latency,
            'max_latency': self.max_latency,
            'avg_latency': self.avg_latency,
            'jitter': self.jitter,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received
        }