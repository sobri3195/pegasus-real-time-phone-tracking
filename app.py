import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, Device, LocationLog, RemoteSession, AccessLog
from security import security_manager, require_token, require_device_access
from location_engine import location_engine
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tracking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour"],
        storage_uri="memory://"
    )
    
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Phone Tracking System API',
            'version': '1.0.0',
            'warning': 'Use only for authorized device tracking',
            'endpoints': {
                'devices': '/api/devices',
                'location': '/api/location',
                'remote_access': '/api/remote_access'
            }
        })
    
    @app.route('/api/devices/register', methods=['POST'])
    @limiter.limit("10 per hour")
    def register_device():
        data = request.json
        
        if not data.get('owner_name'):
            return jsonify({'error': 'Owner name is required'}), 400
        
        if not data.get('consent_verified'):
            return jsonify({'error': 'Owner consent must be verified'}), 400
        
        device_id = data.get('device_id') or security_manager.generate_device_id()
        
        existing_device = Device.query.get(device_id)
        if existing_device:
            return jsonify({'error': 'Device already registered'}), 409
        
        device = Device(
            device_id=device_id,
            owner_name=data['owner_name'],
            consent_verified=True,
            consent_date=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(device)
        db.session.commit()
        
        logger.info(f"Device registered: {device_id}")
        
        return jsonify({
            'message': 'Device registered successfully',
            'device': device.to_dict()
        }), 201
    
    @app.route('/api/devices/<device_id>', methods=['GET'])
    @require_token
    @require_device_access
    def get_device(device_id):
        device = Device.query.get(device_id)
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        return jsonify(device.to_dict())
    
    @app.route('/api/devices/<device_id>', methods=['PUT'])
    @require_token
    @require_device_access
    def update_device(device_id):
        device = Device.query.get(device_id)
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        data = request.json
        
        if 'is_active' in data:
            device.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify(device.to_dict())
    
    @app.route('/api/devices/<device_id>/location', methods=['GET'])
    @require_token
    @require_device_access
    def get_current_location(device_id):
        device = Device.query.get(device_id)
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        latest_location = LocationLog.query.filter_by(
            device_id=device_id
        ).order_by(LocationLog.timestamp.desc()).first()
        
        if not latest_location:
            return jsonify({'error': 'No location data available'}), 404
        
        response = latest_location.to_dict()
        
        address = location_engine.get_address_from_coordinates(
            latest_location.latitude,
            latest_location.longitude
        )
        if address:
            response['address'] = address
        
        return jsonify(response)
    
    @app.route('/api/location/update', methods=['POST'])
    @limiter.limit("120 per hour")
    def update_location():
        data = request.json
        
        device_id = data.get('device_id')
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        device = Device.query.get(device_id)
        if not device:
            return jsonify({'error': 'Device not registered'}), 404
        
        if not device.is_active:
            return jsonify({'error': 'Device tracking is disabled'}), 403
        
        try:
            location_data = location_engine.process_location(data)
        except Exception as e:
            logger.error(f"Location processing error: {str(e)}")
            return jsonify({'error': f'Invalid location data: {str(e)}'}), 400
        
        location_log = LocationLog(
            device_id=device_id,
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            source=location_data['source'],
            accuracy=location_data.get('accuracy'),
            altitude=location_data.get('altitude'),
            speed=location_data.get('speed'),
            battery_level=data.get('battery_level'),
            cell_id=location_data.get('cell_id'),
            lac=location_data.get('lac'),
            signal_strength=data.get('signal_strength')
        )
        
        db.session.add(location_log)
        
        device.last_seen = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Location updated for device {device_id}: {location_data['source']}")
        
        return jsonify({
            'message': 'Location updated successfully',
            'location': location_log.to_dict()
        }), 201
    
    @app.route('/api/location/history/<device_id>', methods=['GET'])
    @require_token
    @require_device_access
    def get_location_history(device_id):
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        device = Device.query.get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        locations = LocationLog.query.filter_by(
            device_id=device_id
        ).order_by(LocationLog.timestamp.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'device_id': device_id,
            'count': len(locations),
            'locations': [loc.to_dict() for loc in locations]
        })
    
    @app.route('/api/remote_access/request', methods=['POST'])
    @limiter.limit("5 per minute")
    def request_remote_access():
        data = request.json
        
        device_id = data.get('device_id')
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        device = Device.query.get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        if not device.consent_verified:
            return jsonify({'error': 'Device owner consent not verified'}), 403
        
        token = security_manager.generate_token(device_id)
        
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        session = RemoteSession(
            session_token=token,
            device_id=device_id,
            expires_at=expires_at,
            ip_address=get_remote_address(),
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(session)
        db.session.commit()
        
        logger.info(f"Remote access token generated for device {device_id} from IP {session.ip_address}")
        
        return jsonify({
            'message': 'Remote access token generated',
            'token': token,
            'expires_at': expires_at.isoformat(),
            'device_id': device_id,
            'warning': 'Token will expire in 24 hours'
        })
    
    @app.route('/api/remote_access/revoke', methods=['POST'])
    @require_token
    def revoke_remote_access():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        session = RemoteSession.query.filter_by(session_token=token).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Remote access token revoked for device {session.device_id}")
        
        return jsonify({'message': 'Token revoked successfully'})
    
    @app.route('/api/remote_access/logs', methods=['GET'])
    @require_token
    @require_device_access
    def get_access_logs():
        device_id = request.args.get('device_id')
        
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        sessions = RemoteSession.query.filter_by(device_id=device_id).all()
        
        logs = []
        for session in sessions:
            session_logs = AccessLog.query.filter_by(session_id=session.id).all()
            logs.extend([log.to_dict() for log in session_logs])
        
        return jsonify({
            'device_id': device_id,
            'count': len(logs),
            'logs': logs
        })
    
    @app.before_request
    def log_request():
        if request.path.startswith('/api/remote_access'):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if token:
                session = RemoteSession.query.filter_by(session_token=token).first()
                
                if session and not session.is_revoked:
                    access_log = AccessLog(
                        session_id=session.id,
                        endpoint=request.path,
                        method=request.method,
                        ip_address=get_remote_address(),
                        user_agent=request.headers.get('User-Agent', '')
                    )
                    db.session.add(access_log)
                    db.session.commit()
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Rate limit exceeded', 'message': str(e.description)}), 429
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    from config import Config
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
