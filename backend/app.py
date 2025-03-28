from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta
import os

from backend.models import db, PingResult
from backend.config import config
from backend.pingTest import ping_test

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    
    # Register API routes
    @app.route('/api/ping-results', methods=['GET'])
    def get_ping_results():
        # Get query parameters for filtering
        hours = request.args.get('hours', default=24, type=int)
        limit = request.args.get('limit', default=1000, type=int)
        
        # Calculate time filter
        time_filter = datetime.utcnow() - timedelta(hours=hours)
        
        # Query database
        results = PingResult.query.filter(
            PingResult.timestamp >= time_filter
        ).order_by(
            PingResult.timestamp.desc()
        ).limit(limit).all()
        
        # Return as JSON
        return jsonify([result.to_dict() for result in results])
    
    @app.route('/api/ping-stats', methods=['GET'])
    def get_ping_stats():
        # Get latest ping result
        latest = PingResult.query.order_by(PingResult.timestamp.desc()).first()
        
        if not latest:
            return jsonify({
                'status': 'error',
                'message': 'No ping results available'
            }), 404
        
        # Calculate 24-hour statistics
        day_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Get average values for the last 24 hours
        day_stats = db.session.query(
            db.func.avg(PingResult.packet_loss).label('avg_packet_loss'),
            db.func.avg(PingResult.avg_latency).label('avg_latency'),
            db.func.avg(PingResult.jitter).label('avg_jitter'),
            db.func.min(PingResult.min_latency).label('min_latency'),
            db.func.max(PingResult.max_latency).label('max_latency')
        ).filter(PingResult.timestamp >= day_ago).first()
        
        return jsonify({
            'latest': latest.to_dict(),
            'day_stats': {
                'avg_packet_loss': day_stats.avg_packet_loss if day_stats.avg_packet_loss else 0,
                'avg_latency': day_stats.avg_latency if day_stats.avg_latency else 0,
                'avg_jitter': day_stats.avg_jitter if day_stats.avg_jitter else 0,
                'min_latency': day_stats.min_latency if day_stats.min_latency else 0,
                'max_latency': day_stats.max_latency if day_stats.max_latency else 0
            }
        })
    
    # Serve the Vue app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    app.run(host='0.0.0.0', port=5000)