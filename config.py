import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tracking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET = os.getenv('JWT_SECRET', 'dev-jwt-secret-change-in-production')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'dev-encryption-key-change-in-production-32bytes')
    
    OPENCELLID_API_KEY = os.getenv('OPENCELLID_API_KEY', '')
    
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True') == 'True'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '5'))
    
    TOKEN_EXPIRATION_HOURS = int(os.getenv('TOKEN_EXPIRATION_HOURS', '24'))
    TOKEN_EXPIRATION = timedelta(hours=TOKEN_EXPIRATION_HOURS)
    
    LOCATION_UPDATE_INTERVAL = int(os.getenv('LOCATION_UPDATE_INTERVAL', '30'))
    BATTERY_THRESHOLD = int(os.getenv('BATTERY_THRESHOLD', '15'))
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'tracking.log')
    
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
