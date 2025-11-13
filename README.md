# Real-Time Phone Tracking System

**⚠️ LEGAL DISCLAIMER / PENAFIAN HUKUM**

This system is designed EXCLUSIVELY for tracking devices with explicit owner consent and authorization. Unauthorized tracking of devices is illegal in most jurisdictions and may result in criminal prosecution.

**ONLY USE THIS SYSTEM IF:**
- You are the legal owner of the device being tracked
- You have written consent from the device owner
- You are legally authorized (parent/guardian, employer with proper agreements, etc.)

**ILLEGAL USES:**
- Tracking someone without their knowledge or consent
- Stalking or harassment
- Corporate espionage
- Any violation of privacy laws

## System Overview

A comprehensive phone tracking system with real-time monitoring, geofencing, alerts, and secure remote access:
- **Real-Time Tracking**: WebSocket-based live updates every 5 seconds
- **Geofencing**: Virtual perimeters with entry/exit notifications (100m-10km radius)
- **Alert System**: Email, push notifications, and webhooks
- **Location History**: 30-day retention with CSV/JSON/KML export
- **Secure Remote Access**: Token-based backdoor access (max 3 tokens/device)
- **Mobile Agent**: Android app with GPS/BTS tracking
- **Legal Compliance**: Built-in consent verification and data retention

## Features

### 1. **Real-Time Tracking**
   - Live map with Leaflet.js integration
   - WebSocket updates every 5 seconds
   - Multi-source location: GPS (3-5m) + BTS (50-200m)
   - Signal indicators (GPS/BTS/Offline)
   - Device status monitoring (battery, speed, signal strength)
   - Interactive dashboard with auto-refresh

### 2. **Geo-Fencing**
   - Create virtual perimeters (100m - 10km radius)
   - Maximum 10 geofences per device
   - Entry/exit event detection
   - Real-time notifications
   - Geofence management (create/update/delete)
   - Event history tracking

### 3. **Location History**
   - 30-day automatic retention
   - Timeline visualization
   - Export formats: CSV, JSON, KML
   - Pagination and filtering
   - Address reverse geocoding
   - Movement pattern analysis

### 4. **Backdoor Secure Access**
   - Token-based remote access (no login required)
   - Maximum 3 active tokens per device
   - 24-hour token validity
   - Complete audit logging (IP, timestamp, user agent)
   - Rate limiting (5 req/min generation, 30 req/min access)
   - Automatic cleanup of expired tokens

### 5. **Alert System**
   - **Triggers**: Geofence entry/exit, device offline (>1h), GPS loss (>5min), remote access attempts
   - **Channels**: Email (SMTP), Push notifications (FCM), Webhooks (Slack/Telegram/Discord)
   - **Management**: Configure per-device, enable/disable, severity levels
   - **History**: View and filter alerts, mark as read

### 6. **Android Mobile Agent**
   - Background location tracking with foreground service
   - GPS + BTS triangulation
   - Battery-aware operation (pauses at <15%)
   - Configurable update intervals (default: 30s)
   - Network state detection and retry logic
   - Consent verification on first launch

## Technology Stack

- **Backend**: Flask 2.3.3, Flask-SocketIO, Flask-CORS
- **Real-time**: Socket.IO with eventlet
- **Database**: SQLite (development) / PostgreSQL (production)
- **Security**: JWT, AES-256, bcrypt
- **Location**: geopy, OpenCellID API
- **Calculations**: scipy (trilateration), Haversine (geofencing)
- **Notifications**: SMTP (email), Firebase (push), Webhooks
- **Frontend**: Leaflet.js (maps), Socket.IO client
- **Mobile**: Android (Kotlin), Min SDK 24

## Installation

```bash
# Clone repository
git clone <repository-url>
cd project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Run server
python app.py
```

## Configuration

Edit `.env` file:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///tracking.db  # or postgresql://...
OPENCELLID_API_KEY=your-opencellid-api-key
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-32-byte-encryption-key
FLASK_ENV=development
```

## Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your settings

# 3. Initialize
python init_db.py

# 4. Run server
python app.py

# 5. Open dashboard
# Visit: http://localhost:5000/dashboard
```

## API Endpoints

### Device Management
- `POST /api/devices/register` - Register a new device
- `GET /api/devices/<device_id>` - Get device information
- `PUT /api/devices/<device_id>` - Update device settings

### Location Tracking
- `POST /api/update_location` - Update location (mobile agent)
- `POST /api/location/update` - Alternative update endpoint
- `GET /api/get_location?device_id=xxx` - Get current location
- `GET /api/devices/<device_id>/location` - Alternative get endpoint
- `GET /api/location/history/<device_id>` - Get location history
- `GET /api/location/history/<device_id>/export` - Export (CSV/JSON/KML)

### Geofencing
- `POST /api/geofences` - Create geofence
- `GET /api/geofences/<device_id>` - List geofences
- `PUT /api/geofences/<geofence_id>` - Update geofence
- `DELETE /api/geofences/<geofence_id>` - Delete geofence
- `GET /api/geofences/<device_id>/events` - Get entry/exit events

### Alerts
- `GET /api/alerts/<device_id>` - Get alerts
- `PUT /api/alerts/<alert_id>/read` - Mark alert as read
- `POST /api/alerts/config` - Configure alert settings
- `GET /api/alerts/config/<device_id>` - Get alert configs

### Remote Access (Backdoor)
- `POST /api/remote_access/generate` - Generate access token
- `POST /api/remote_access/request` - Alternative generate endpoint
- `GET /api/remote_access/location?token=xxx` - Access location via token
- `POST /api/remote_access/revoke` - Revoke access token
- `GET /api/remote_access/logs` - View access audit logs

### WebSocket Events
- `connect` - Connect to real-time server
- `subscribe` - Subscribe to device updates
- `location_update` - Receive location updates (every 5s)
- `request_location` - Request immediate location

**Full API Documentation:** See [API_ENDPOINTS.md](API_ENDPOINTS.md)

## Security Features

1. **Authentication**: JWT tokens with expiration
2. **Encryption**: AES-256 for sensitive data
3. **Rate Limiting**: Prevents abuse and DoS attacks
4. **Audit Logging**: All remote access attempts logged
5. **Token Rotation**: Automatic expiration after 24 hours

## Mobile Agent Setup

See `mobile_agent/README.md` for Android app setup instructions.

## Development

```bash
# Run tests
pytest tests/

# Check code quality
flake8 .
black .

# Run with debug mode
python app.py --debug
```

## Data Retention & Cleanup

Automatic data retention policy:
- Location logs: **30 days** (auto-delete)
- Expired tokens: Auto-cleanup on startup
- Read alerts: Deleted with old data
- Access logs: 90 days retention

Manual cleanup:
```bash
# Dry run (check what would be deleted)
python cleanup_old_data.py --dry-run

# Clean data older than 30 days
python cleanup_old_data.py --days 30

# Include access log cleanup (90+ days)
python cleanup_old_data.py --access-logs
```

Setup automated cleanup (cron):
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/project && /path/to/venv/bin/python cleanup_old_data.py
```

## Legal Compliance

This system includes:
- **Consent verification**: Pop-up on mobile agent, email/phone verification
- **Legal disclaimer**: Prominently displayed on dashboard
- **Activity audit trails**: Complete IP, timestamp, endpoint logging
- **Data retention policies**: 30-day auto-deletion
- **User rights**: View, export, delete personal data
- **GDPR compliance**: Data minimization, purpose limitation
- **Alert notifications**: Remote access attempt logging

**⚠️ Consult with legal counsel before deployment in any jurisdiction.**

## Documentation

- **[README.md](README.md)** - This file (getting started)
- **[API_ENDPOINTS.md](API_ENDPOINTS.md)** - Complete API reference
- **[FEATURES.md](FEATURES.md)** - Detailed feature documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[SECURITY.md](SECURITY.md)** - Security guidelines
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Original API docs

## Project Structure

```
/
├── app.py                      # Main Flask application with WebSocket
├── models.py                   # Database models (Device, Location, Geofence, Alert)
├── security.py                 # JWT, encryption, authentication
├── location_engine.py          # GPS/BTS processing & trilateration
├── geofencing.py              # Geofence detection & management
├── notifications.py           # Email/Push/Webhook alert system
├── config.py                  # Configuration management
├── cleanup_old_data.py        # Data retention cleanup script
├── init_db.py                 # Database initialization
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── templates/
│   └── dashboard.html         # Web dashboard UI
├── mobile_agent/              # Android tracking app
├── tests/                     # Unit tests
└── scripts/                   # Helper scripts
```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or concerns, please open an issue on the repository.

---

## Version History

- **v2.0** (Current) - Real-time tracking, geofencing, alerts, remote access
- **v1.0** - Basic GPS/BTS tracking with API

---

## Author

**Lettu Kes dr. Muhammad Sobri Maulana, S.Kom, CEH, OSCP, OSCE**

- 📧 Email: [muhammadsobrimaulana31@gmail.com](mailto:muhammadsobrimaulana31@gmail.com)
- 💻 GitHub: [github.com/sobri3195](https://github.com/sobri3195)
- 🌐 Website: [muhammadsobrimaulana.netlify.app](https://muhammadsobrimaulana.netlify.app)

### Connect with Me

- 📺 YouTube: [@muhammadsobrimaulana6013](https://www.youtube.com/@muhammadsobrimaulana6013)
- 📱 TikTok: [@dr.sobri](https://www.tiktok.com/@dr.sobri)
- 💬 Telegram: [winlin_exploit](https://t.me/winlin_exploit)
- 💬 WhatsApp Group: [Join Community](https://chat.whatsapp.com/B8nwRZOBMo64GjTwdXV8Bl)

### Support My Work

If you find this project helpful, consider supporting me:

- ☕ Trakteer: [trakteer.id/g9mkave5gauns962u07t](https://trakteer.id/g9mkave5gauns962u07t)
- 💳 Lynk: [lynk.id/muhsobrimaulana](https://lynk.id/muhsobrimaulana)
- 🎨 KaryaKarsa: [karyakarsa.com/muhammadsobrimaulana](https://karyakarsa.com/muhammadsobrimaulana)
- 💰 Nyawer: [nyawer.co/MuhammadSobriMaulana](https://nyawer.co/MuhammadSobriMaulana)
- 🛒 Gumroad: [maulanasobri.gumroad.com](https://maulanasobri.gumroad.com/)
- 🌐 Portfolio: [muhammad-sobri-maulana-kvr6a.sevalla.page](https://muhammad-sobri-maulana-kvr6a.sevalla.page/)

---

**Remember: With great power comes great responsibility. Use ethically and legally.**
