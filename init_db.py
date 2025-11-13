#!/usr/bin/env python3
import os
from app import create_app
from models import db

def init_database():
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database initialized successfully!")
        
        print("\nDatabase schema:")
        print("- devices: Store device information and consent")
        print("- location_logs: Store location history")
        print("- remote_sessions: Store remote access tokens")
        print("- access_logs: Store access audit logs")
        print("\n✓ Ready to track devices with owner consent")


if __name__ == '__main__':
    init_database()
