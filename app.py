import os
import io
import csv
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from models import (db, Device, LocationLog, RemoteSession, AccessLog, 
                    Geofence, GeofenceEvent, AlertConfig, Alert)
from security import security_manager, require_token, require_device_access
from location_engine import location_engine
from geofencing import geofence_manager
from notifications import notification_manager
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
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    CORS(app)
    db.init_app(app)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour"],
        storage_uri="memory://"
    )
    
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")
        
        from sqlalchemy import text
        try:
            db.session.execute(text("DELETE FROM location_logs WHERE timestamp < datetime('now', '-30 days')"))
            db.session.commit()
            logger.info("Cleaned up old location data (30+ days)")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Phone Tracking System API',
            'version': '2.0.0',
            'warning': 'Use only for authorized device tracking',
            'dashboard': '/dashboard',
            'endpoints': {
                'devices': '/api/devices',
                'location': '/api/location',
                'geofences': '/api/geofences',
                'alerts': '/api/alerts',
                'remote_access': '/api/remote_access'
            }
        })
    
    @app.route('/dashboard')
    def dashboard():
        from flask import render_template
        return render_template('dashboard.html')
    
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
    
    @app.route('/api/get_location', methods=['GET'])
    @limiter.limit("60 per hour")
    def get_location_alt():
        device_id = request.args.get('device_id')
        if not device_id:
            return jsonify({'error': 'device_id parameter is required'}), 400
        return get_current_location(device_id)
    
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
    
    @app.route('/api/update_location', methods=['POST'])
    @limiter.limit("120 per hour")
    def update_location_alt():
        return update_location()
    
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
        
        geofence_events = geofence_manager.check_geofences(
            device_id, location_data['latitude'], location_data['longitude']
        )
        
        for event in geofence_events:
            geofence = Geofence.query.get(event.geofence_id)
            if geofence:
                notification_manager.notify_geofence_event(
                    device_id, geofence.name, event.event_type
                )
        
        socketio.emit('location_update', {
            'device_id': device_id,
            'location': location_log.to_dict(),
            'geofence_events': [e.to_dict() for e in geofence_events]
        }, room=f'device_{device_id}')
        
        logger.info(f"Location updated for device {device_id}: {location_data['source']}")
        
        return jsonify({
            'message': 'Location updated successfully',
            'location': location_log.to_dict(),
            'geofence_events': [e.to_dict() for e in geofence_events]
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
    
    @app.route('/api/location/history/<device_id>/export', methods=['GET'])
    @require_token
    @require_device_access
    def export_location_history(device_id):
        export_format = request.args.get('format', 'csv')
        days = request.args.get('days', 30, type=int)
        
        device = Device.query.get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        locations = LocationLog.query.filter(
            LocationLog.device_id == device_id,
            LocationLog.timestamp >= cutoff_date
        ).order_by(LocationLog.timestamp.desc()).all()
        
        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Source', 'Accuracy', 
                           'Speed', 'Battery', 'Signal Strength'])
            
            for loc in locations:
                writer.writerow([
                    loc.timestamp.isoformat(),
                    loc.latitude,
                    loc.longitude,
                    loc.source,
                    loc.accuracy,
                    loc.speed,
                    loc.battery_level,
                    loc.signal_strength
                ])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{device_id}_history.csv'
            )
        
        elif export_format == 'json':
            data = {
                'device_id': device_id,
                'export_date': datetime.utcnow().isoformat(),
                'locations': [loc.to_dict() for loc in locations]
            }
            return jsonify(data)
        
        elif export_format == 'kml':
            kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Device {device_id} Location History</name>
    <description>Location tracking data</description>
'''
            for loc in locations:
                kml += f'''    <Placemark>
      <name>{loc.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</name>
      <description>Source: {loc.source}, Accuracy: {loc.accuracy}m</description>
      <Point>
        <coordinates>{loc.longitude},{loc.latitude},0</coordinates>
      </Point>
    </Placemark>
'''
            kml += '''  </Document>
</kml>'''
            
            return send_file(
                io.BytesIO(kml.encode()),
                mimetype='application/vnd.google-earth.kml+xml',
                as_attachment=True,
                download_name=f'{device_id}_history.kml'
            )
        
        return jsonify({'error': 'Invalid format. Use csv, json, or kml'}), 400
    
    @app.route('/api/geofences', methods=['POST'])
    @require_token
    @limiter.limit("20 per hour")
    def create_geofence():
        data = request.json
        
        required_fields = ['device_id', 'name', 'latitude', 'longitude', 'radius']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        device = Device.query.get(data['device_id'])
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        active_geofences = Geofence.query.filter_by(
            device_id=data['device_id'], is_active=True
        ).count()
        
        if active_geofences >= 10:
            return jsonify({'error': 'Maximum 10 active geofences per device'}), 400
        
        try:
            geofence = geofence_manager.create_geofence(
                device_id=data['device_id'],
                name=data['name'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                radius=data['radius'],
                notify_on_enter=data.get('notify_on_enter', True),
                notify_on_exit=data.get('notify_on_exit', True)
            )
            
            return jsonify({
                'message': 'Geofence created successfully',
                'geofence': geofence.to_dict()
            }), 201
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/geofences/<device_id>', methods=['GET'])
    @require_token
    @require_device_access
    def get_geofences(device_id):
        geofences = geofence_manager.get_geofences(device_id)
        return jsonify({
            'device_id': device_id,
            'geofences': [g.to_dict() for g in geofences]
        })
    
    @app.route('/api/geofences/<int:geofence_id>', methods=['PUT'])
    @require_token
    def update_geofence(geofence_id):
        data = request.json
        geofence = geofence_manager.update_geofence(geofence_id, **data)
        
        if not geofence:
            return jsonify({'error': 'Geofence not found'}), 404
        
        return jsonify(geofence.to_dict())
    
    @app.route('/api/geofences/<int:geofence_id>', methods=['DELETE'])
    @require_token
    def delete_geofence(geofence_id):
        if geofence_manager.delete_geofence(geofence_id):
            return jsonify({'message': 'Geofence deleted successfully'})
        return jsonify({'error': 'Geofence not found'}), 404
    
    @app.route('/api/geofences/<device_id>/events', methods=['GET'])
    @require_token
    @require_device_access
    def get_geofence_events(device_id):
        limit = request.args.get('limit', 100, type=int)
        events = GeofenceEvent.query.filter_by(
            device_id=device_id
        ).order_by(GeofenceEvent.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'device_id': device_id,
            'events': [e.to_dict() for e in events]
        })
    
    @app.route('/api/alerts/<device_id>', methods=['GET'])
    @require_token
    @require_device_access
    def get_alerts(device_id):
        limit = request.args.get('limit', 50, type=int)
        alerts = Alert.query.filter_by(
            device_id=device_id
        ).order_by(Alert.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'device_id': device_id,
            'alerts': [a.to_dict() for a in alerts]
        })
    
    @app.route('/api/alerts/<int:alert_id>/read', methods=['PUT'])
    @require_token
    def mark_alert_read(alert_id):
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.is_read = True
        db.session.commit()
        
        return jsonify(alert.to_dict())
    
    @app.route('/api/alerts/config', methods=['POST'])
    @require_token
    def create_alert_config():
        data = request.json
        
        if not data.get('device_id') or not data.get('alert_type'):
            return jsonify({'error': 'device_id and alert_type are required'}), 400
        
        config = AlertConfig(
            device_id=data['device_id'],
            alert_type=data['alert_type'],
            enabled=data.get('enabled', True),
            email_enabled=data.get('email_enabled', False),
            push_enabled=data.get('push_enabled', False),
            webhook_url=data.get('webhook_url')
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify(config.to_dict()), 201
    
    @app.route('/api/alerts/config/<device_id>', methods=['GET'])
    @require_token
    @require_device_access
    def get_alert_configs(device_id):
        configs = AlertConfig.query.filter_by(device_id=device_id).all()
        return jsonify({
            'device_id': device_id,
            'configs': [c.to_dict() for c in configs]
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
        
        active_tokens = RemoteSession.query.filter_by(
            device_id=device_id,
            is_revoked=False
        ).filter(RemoteSession.expires_at > datetime.utcnow()).count()
        
        if active_tokens >= 3:
            return jsonify({'error': 'Maximum 3 active tokens per device. Please revoke an existing token first.'}), 400
        
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
        
        notification_manager.notify_remote_access_attempt(device_id, get_remote_address())
        
        logger.info(f"Remote access token generated for device {device_id} from IP {session.ip_address}")
        
        return jsonify({
            'message': 'Remote access token generated',
            'token': token,
            'expires_at': expires_at.isoformat(),
            'device_id': device_id,
            'warning': 'Token will expire in 24 hours'
        })
    
    @app.route('/api/remote_access/generate', methods=['POST'])
    @limiter.limit("5 per minute")
    def generate_remote_access():
        return request_remote_access()
    
    @app.route('/api/remote_access/location', methods=['GET'])
    @limiter.limit("30 per minute")
    def get_remote_location():
        token = request.args.get('token')
        
        if not token:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 401
        
        session = RemoteSession.query.filter_by(session_token=token).first()
        
        if not session:
            return jsonify({'error': 'Invalid token'}), 401
        
        if session.is_revoked:
            return jsonify({'error': 'Token has been revoked'}), 401
        
        if session.expires_at < datetime.utcnow():
            return jsonify({'error': 'Token has expired'}), 401
        
        device = Device.query.get(session.device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        latest_location = LocationLog.query.filter_by(
            device_id=session.device_id
        ).order_by(LocationLog.timestamp.desc()).first()
        
        if not latest_location:
            return jsonify({'error': 'No location data available'}), 404
        
        access_log = AccessLog(
            session_id=session.id,
            endpoint='/api/remote_access/location',
            method='GET',
            ip_address=get_remote_address(),
            user_agent=request.headers.get('User-Agent', ''),
            status_code=200
        )
        db.session.add(access_log)
        db.session.commit()
        
        return jsonify({
            'device_id': session.device_id,
            'location': latest_location.to_dict(),
            'device_status': {
                'is_active': device.is_active,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None
            }
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
    
    @socketio.on('connect')
    def handle_connect():
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {'status': 'Connected to tracking server'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        device_id = data.get('device_id')
        if device_id:
            join_room(f'device_{device_id}')
            logger.info(f"Client {request.sid} subscribed to device {device_id}")
            emit('subscribed', {'device_id': device_id, 'status': 'success'})
        else:
            emit('error', {'message': 'device_id is required'})
    
    @socketio.on('request_location')
    def handle_request_location(data):
        device_id = data.get('device_id')
        if not device_id:
            emit('error', {'message': 'device_id is required'})
            return
        
        latest_location = LocationLog.query.filter_by(
            device_id=device_id
        ).order_by(LocationLog.timestamp.desc()).first()
        
        if latest_location:
            emit('location_update', {
                'device_id': device_id,
                'location': latest_location.to_dict()
            })
        else:
            emit('error', {'message': 'No location data available'})
    
    app.socketio = socketio
    return app


if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    from config import Config
    app.socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
