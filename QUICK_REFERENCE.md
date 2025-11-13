# Quick Reference Guide

## 🚀 Quick Start

```bash
# Setup
./quickstart.sh

# Run server
source venv/bin/activate
python app.py
```

## 📋 File Structure

```
Core Backend
├── app.py              - Main Flask application
├── config.py           - Configuration
├── models.py           - Database models
├── security.py         - JWT & encryption
└── location_engine.py  - GPS/BTS processing

Mobile
└── mobile_agent/
    ├── MainActivity.kt
    └── LocationTrackingService.kt

Documentation
├── README.md           - Getting started
├── API_DOCUMENTATION.md - API reference
├── DEPLOYMENT.md       - Production guide
├── SECURITY.md         - Security policies
└── PROJECT_SUMMARY.md  - Complete overview
```

## 🔑 Essential Commands

### Setup
```bash
python scripts/generate_keys.py  # Generate keys
python init_db.py                # Initialize DB
pip install -r requirements.txt  # Install deps
```

### Development
```bash
python app.py                    # Run server
pytest tests/                    # Run tests
python scripts/test_api.py       # Test API
python client_example.py         # Demo client
```

### Android
```bash
cd mobile_agent
./gradlew assembleDebug          # Build APK
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 🔌 API Quick Reference

### Device Registration
```bash
curl -X POST http://localhost:5000/api/devices/register \
  -H "Content-Type: application/json" \
  -d '{"owner_name":"John Doe","consent_verified":true}'
```

### Get Access Token
```bash
curl -X POST http://localhost:5000/api/remote_access/request \
  -H "Content-Type: application/json" \
  -d '{"device_id":"YOUR_DEVICE_ID"}'
```

### Update Location
```bash
curl -X POST http://localhost:5000/api/location/update \
  -H "Content-Type: application/json" \
  -d '{
    "device_id":"YOUR_DEVICE_ID",
    "source":"GPS",
    "latitude":37.7749,
    "longitude":-122.4194,
    "accuracy":5.0
  }'
```

### Get Current Location
```bash
curl -X GET http://localhost:5000/api/devices/YOUR_DEVICE_ID/location \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🐍 Python Client Example

```python
from client_example import TrackingClient

# Initialize
client = TrackingClient("http://localhost:5000")

# Register device
result = client.register_device("John Doe")
device_id = result["device"]["device_id"]

# Get token
token = client.request_access_token(device_id)

# Update location
client.update_location(37.7749, -122.4194, accuracy=5.0)

# Get current location
location = client.get_current_location()
print(f"Location: {location['latitude']}, {location['longitude']}")
```

## 🗄️ Database Schema

```sql
-- Devices
CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    owner_name TEXT NOT NULL,
    consent_verified BOOLEAN,
    last_seen TIMESTAMP,
    is_active BOOLEAN
);

-- Location Logs
CREATE TABLE location_logs (
    id INTEGER PRIMARY KEY,
    device_id TEXT,
    latitude REAL,
    longitude REAL,
    source TEXT,  -- 'GPS' or 'BTS'
    accuracy REAL,
    timestamp TIMESTAMP
);

-- Remote Sessions
CREATE TABLE remote_sessions (
    id INTEGER PRIMARY KEY,
    session_token TEXT UNIQUE,
    device_id TEXT,
    expires_at TIMESTAMP,
    ip_address TEXT
);
```

## 🔒 Security Checklist

- [ ] Generated strong keys (`python scripts/generate_keys.py`)
- [ ] Updated `.env` with real keys
- [ ] HTTPS enabled in production
- [ ] Firewall configured
- [ ] Database password set
- [ ] OpenCellID API key configured
- [ ] Debug mode disabled in production

## ⚙️ Configuration

### Key Environment Variables

```env
SECRET_KEY=<generate-with-script>
JWT_SECRET=<generate-with-script>
ENCRYPTION_KEY=<generate-with-script>
OPENCELLID_API_KEY=<from-opencellid.org>
DATABASE_URL=sqlite:///tracking.db
RATE_LIMIT_PER_MINUTE=5
TOKEN_EXPIRATION_HOURS=24
```

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_security.py -v

# With coverage
pytest --cov=. tests/

# API tests
python scripts/test_api.py
```

## 📊 Monitoring

### Logs
```bash
# Application logs
tail -f tracking.log

# Systemd logs (production)
journalctl -u phone-tracking -f

# Nginx logs
tail -f /var/log/nginx/access.log
```

### Database
```bash
# SQLite
sqlite3 tracking.db "SELECT COUNT(*) FROM location_logs;"

# PostgreSQL
psql -d tracking_db -c "SELECT COUNT(*) FROM location_logs;"
```

## 🚨 Troubleshooting

### Server won't start
```bash
# Check logs
cat tracking.log

# Verify database
python init_db.py

# Check dependencies
pip install -r requirements.txt
```

### Location not updating
```bash
# Check device registration
curl http://localhost:5000/api/devices/DEVICE_ID \
  -H "Authorization: Bearer TOKEN"

# Verify OpenCellID key
echo $OPENCELLID_API_KEY

# Check mobile app permissions
adb logcat | grep LocationTracking
```

### Authentication errors
```bash
# Verify token
python -c "from security import security_manager; \
  print(security_manager.verify_token('YOUR_TOKEN'))"

# Generate new token
curl -X POST http://localhost:5000/api/remote_access/request \
  -d '{"device_id":"DEVICE_ID"}'
```

## 📱 Android Debugging

```bash
# View logs
adb logcat | grep LocationTracking

# Install app
adb install -r app-debug.apk

# Check permissions
adb shell dumpsys package com.tracking.agent | grep permission

# Test location
adb shell am start -a android.intent.action.VIEW \
  -d "geo:37.7749,-122.4194"
```

## 🔗 Important URLs

- **API Base**: `http://localhost:5000/api`
- **OpenCellID**: https://opencellid.org/
- **Documentation**: See `*.md` files in project root

## 📞 Support

- **Docs**: `README.md`, `API_DOCUMENTATION.md`
- **Security**: `SECURITY.md`
- **Deployment**: `DEPLOYMENT.md`
- **Contributing**: `CONTRIBUTING.md`

## ⚠️ Legal Reminder

**ONLY track devices with explicit owner consent!**

Unauthorized tracking is illegal and unethical.

---

**Quick Links:**
- [Complete Setup](README.md#installation)
- [API Reference](API_DOCUMENTATION.md)
- [Security Guide](SECURITY.md)
- [Deployment](DEPLOYMENT.md)
