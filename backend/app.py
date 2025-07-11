from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta
import os

from backend.models import db, PingResult, configure_schema_if_postgres
from backend.config import config
# ping_test import removed as it's unused

def get_rounded_time(hours=0):
    """Get current time with optional hour offset.
    
    This helper function takes the current UTC time and subtracts the specified
    number of hours to create a time window for data queries.
    
    Args:
        hours: Number of hours to subtract from the current time (default: 0)
    
    Returns:
        datetime: UTC datetime, offset by specified hours
    """
    # Always use UTC for consistency across timezones
    now = datetime.utcnow()
    
    # Apply hour offset directly without rounding
    # This ensures we get the exact time window requested
    if hours > 0:
        time_filter = now - timedelta(hours=hours)
    else:
        time_filter = now
        
    return time_filter

def create_app(config_name='default'):
    """Create and configure the Flask application.
    
    This is the application factory pattern. It creates a new Flask instance,
    loads the configuration, initializes extensions, and registers routes.
    
    Args:
        config_name: Configuration profile to use ('default', 'development', 'production', 'testing')
        
    Returns:
        Configured Flask application instance
    """
    # Initialize Flask app with static files from the Vue.js build directory
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    app.config.from_object(config[config_name])
    
    # Configure PostgreSQL schema if using Postgres (not for SQLite in testing/development)
    configure_schema_if_postgres(app)
    
    # Initialize database, migrations, and cross-origin resource sharing
    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    
    # Register API routes
    @app.route('/api/ping-results', methods=['GET'])
    def get_ping_results():
        """Get network ping test results from the database.
        
        Query parameters:
            hours: Number of hours of history to retrieve (default: 24)
            limit: Maximum number of results to return (default: 1000)
            
        Returns:
            JSON array of ping test results within the specified time range
        """
        # Parse query parameters with defaults
        hours = request.args.get('hours', default=24, type=int)
        # limit parameter kept for API compatibility but not used in query
        limit = request.args.get('limit', default=1000, type=int)
        
        # Use helper function to get rounded time with specified offset
        time_filter = get_rounded_time(hours=hours)
        
        # Query database - get all results in chronological order
        # Remove limit to ensure we get the full time range requested
        results = PingResult.query.filter(
            PingResult.timestamp >= time_filter
        ).order_by(
            PingResult.timestamp.asc()
        ).all()
        
        # Return as JSON
        return jsonify([result.to_dict() for result in results])
    
    @app.route('/api/ping-stats', methods=['GET'])
    def get_ping_stats():
        """Get summary statistics for network performance.
        
        Returns:
            JSON object containing:
            - The most recent ping test result
            - Statistical aggregates for the last 24 hours (avg/max/min metrics)
            
        Status codes:
            200: Success
            404: No ping results available in the database
        """
        # Get the most recent ping test result for current status
        latest = PingResult.query.order_by(PingResult.timestamp.desc()).first()
        
        if not latest:
            return jsonify({
                'status': 'error',
                'message': 'No ping results available'
            }), 404
        
        # Use helper function to get 24 hours ago
        day_ago = get_rounded_time(hours=24)
        
        # Get statistical values for the last 24 hours
        day_stats = db.session.query(
            db.func.avg(PingResult.packet_loss).label('avg_packet_loss'),
            db.func.max(PingResult.packet_loss).label('max_packet_loss'),
            db.func.avg(PingResult.avg_latency).label('avg_latency'),
            db.func.avg(PingResult.jitter).label('avg_jitter'),
            db.func.min(PingResult.min_latency).label('min_latency'),
            db.func.max(PingResult.max_latency).label('max_latency')
        ).filter(PingResult.timestamp >= day_ago).first()
        
        return jsonify({
            'latest': latest.to_dict(),
            'day_stats': {
                'avg_packet_loss': day_stats.avg_packet_loss if day_stats and day_stats.avg_packet_loss else 0,
                'max_packet_loss': day_stats.max_packet_loss if day_stats and day_stats.max_packet_loss else 0,
                'avg_latency': day_stats.avg_latency if day_stats and day_stats.avg_latency else 0,
                'avg_jitter': day_stats.avg_jitter if day_stats and day_stats.avg_jitter else 0,
                'min_latency': day_stats.min_latency if day_stats and day_stats.min_latency else 0,
                'max_latency': day_stats.max_latency if day_stats and day_stats.max_latency else 0
            }
        })
    
    # Serve the Vue.js frontend application
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        """Catch-all route to serve the single-page Vue.js application.
        
        This enables client-side routing by sending all unmatched routes
        to the Vue.js application which handles routing internally.
        """
        return app.send_static_file('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    app.run(host='0.0.0.0', port=5000)