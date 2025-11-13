import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from functools import wraps
from flask import request, jsonify
from config import Config


class SecurityManager:
    def __init__(self, app=None):
        self.app = app
        self.jwt_secret = Config.JWT_SECRET
        self.encryption_key = self._derive_encryption_key(Config.ENCRYPTION_KEY)
        self.fernet = Fernet(self.encryption_key)
    
    def _derive_encryption_key(self, password: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'tracking_system_salt',
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def generate_token(self, device_id: str, expires_in_hours: int = 24) -> str:
        payload = {
            'device_id': device_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(32)
        }
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    def encrypt_data(self, data: str) -> str:
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def hash_device_id(self, device_id: str) -> str:
        return hashlib.sha256(device_id.encode()).hexdigest()
    
    def generate_device_id(self) -> str:
        return secrets.token_urlsafe(32)


security_manager = SecurityManager()


def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        result = security_manager.verify_token(token)
        
        if not result['valid']:
            return jsonify({'error': result.get('error', 'Invalid token')}), 401
        
        request.token_payload = result['payload']
        return f(*args, **kwargs)
    
    return decorated_function


def require_device_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        device_id = kwargs.get('device_id') or request.json.get('device_id')
        token_device_id = request.token_payload.get('device_id')
        
        if device_id != token_device_id:
            return jsonify({'error': 'Unauthorized access to device'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
