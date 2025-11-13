#!/usr/bin/env python3
"""
Installation Test Script
Verify that all dependencies and modules are correctly installed
"""

import sys

def check_import(module_name, package_name=None):
    """Try importing a module and report success/failure"""
    try:
        __import__(module_name)
        print(f"✓ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"✗ {package_name or module_name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("  INSTALLATION TEST")
    print("=" * 60)
    
    print("\nChecking Python version...")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("⚠ Warning: Python 3.9+ recommended")
    else:
        print("✓ Python version OK")
    
    print("\nChecking core dependencies...")
    all_ok = True
    
    dependencies = [
        ("flask", "Flask"),
        ("flask_sqlalchemy", "Flask-SQLAlchemy"),
        ("flask_limiter", "Flask-Limiter"),
        ("flask_socketio", "Flask-SocketIO"),
        ("flask_cors", "Flask-CORS"),
        ("socketio", "python-socketio"),
        ("geopy", "geopy"),
        ("requests", "requests"),
        ("scipy", "scipy"),
        ("numpy", "numpy"),
        ("jwt", "PyJWT"),
        ("cryptography", "cryptography"),
        ("dotenv", "python-dotenv"),
        ("bcrypt", "bcrypt"),
        ("eventlet", "eventlet"),
    ]
    
    for module, package in dependencies:
        if not check_import(module, package):
            all_ok = False
    
    print("\nChecking project modules...")
    project_modules = [
        ("models", "models.py"),
        ("security", "security.py"),
        ("location_engine", "location_engine.py"),
        ("geofencing", "geofencing.py"),
        ("notifications", "notifications.py"),
        ("config", "config.py"),
    ]
    
    for module, filename in project_modules:
        if not check_import(module, filename):
            all_ok = False
    
    print("\nChecking database connectivity...")
    try:
        from app import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✓ Database connection OK")
            
            from models import Device, LocationLog, RemoteSession, Geofence, Alert
            print("✓ All models loaded")
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("  ✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Run the server: python app.py")
        print("  2. Open dashboard: http://localhost:5000/dashboard")
        print("  3. Test API: python example_usage.py")
        return 0
    else:
        print("  ✗ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
