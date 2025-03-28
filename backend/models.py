from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.schema import MetaData
from backend.config import config

# Create a custom MetaData object with the schema name
metadata = MetaData(schema=config['default'].POSTGRES_SCHEMA)

# Initialize SQLAlchemy with the custom metadata
db = SQLAlchemy(metadata=metadata)

class PingResult(db.Model):
    __tablename__ = 'ping_results'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    target = db.Column(db.String(50), nullable=False)
    packet_loss = db.Column(db.Float, nullable=False)
    min_latency = db.Column(db.Float)
    max_latency = db.Column(db.Float)
    avg_latency = db.Column(db.Float)
    jitter = db.Column(db.Float)
    packets_sent = db.Column(db.Integer, nullable=False)
    packets_received = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'target': self.target,
            'packet_loss': self.packet_loss,
            'min_latency': self.min_latency,
            'max_latency': self.max_latency,
            'avg_latency': self.avg_latency,
            'jitter': self.jitter,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received
        }