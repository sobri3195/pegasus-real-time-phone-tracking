from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Device(db.Model):
    __tablename__ = 'devices'
    
    device_id = db.Column(db.String(255), primary_key=True)
    owner_name = db.Column(db.String(255), nullable=False)
    consent_verified = db.Column(db.Boolean, default=False, nullable=False)
    consent_date = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    location_logs = db.relationship('LocationLog', backref='device', lazy=True, cascade='all, delete-orphan')
    remote_sessions = db.relationship('RemoteSession', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'device_id': self.device_id,
            'owner_name': self.owner_name,
            'consent_verified': self.consent_verified,
            'consent_date': self.consent_date.isoformat() if self.consent_date else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LocationLog(db.Model):
    __tablename__ = 'location_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(255), db.ForeignKey('devices.device_id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50), nullable=False)
    accuracy = db.Column(db.Float)
    altitude = db.Column(db.Float)
    speed = db.Column(db.Float)
    battery_level = db.Column(db.Integer)
    cell_id = db.Column(db.String(50))
    lac = db.Column(db.String(50))
    signal_strength = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'source': self.source,
            'accuracy': self.accuracy,
            'altitude': self.altitude,
            'speed': self.speed,
            'battery_level': self.battery_level,
            'cell_id': self.cell_id,
            'lac': self.lac,
            'signal_strength': self.signal_strength,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class RemoteSession(db.Model):
    __tablename__ = 'remote_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(500), unique=True, nullable=False)
    device_id = db.Column(db.String(255), db.ForeignKey('devices.device_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    is_revoked = db.Column(db.Boolean, default=False)
    revoked_at = db.Column(db.DateTime)
    
    access_logs = db.relationship('AccessLog', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'ip_address': self.ip_address,
            'is_revoked': self.is_revoked,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None
        }


class AccessLog(db.Model):
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('remote_sessions.id'), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    status_code = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'ip_address': self.ip_address,
            'status_code': self.status_code,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
