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

A comprehensive phone tracking system with:
- **GPS Tracking**: Real-time location via geopy
- **BTS Triangulation**: Fallback positioning via OpenCellID
- **Secure Remote Access**: JWT-based authentication with AES-256 encryption
- **Mobile Agent**: Android app for data collection
- **Rate Limiting**: Protection against abuse

## Features

1. **Multi-Source Location Tracking**
   - Primary: GPS (3-5m accuracy)
   - Fallback: BTS Triangulation (50-200m accuracy)
   - Smart data fusion with priority handling

2. **Secure Remote Access**
   - JWT token-based authentication
   - AES-256 encrypted data transmission
   - Auto-expiring sessions (24 hours)
   - Rate limiting (5 requests/minute)
   - Complete activity logging

3. **Android Mobile Agent**
   - GPS location collection
   - BTS cell tower information
   - 30-second update intervals
   - Battery-aware operation (pauses at <15%)

## Technology Stack

- **Backend**: Python 3.9+ with Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Security**: JWT, AES-256, bcrypt
- **Location**: geopy, OpenCellID API
- **Calculations**: scipy (trilateration)
- **Mobile**: Android (Java/Kotlin)

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

## API Endpoints

### Device Management
- `POST /api/devices/register` - Register a new device
- `GET /api/devices/<device_id>` - Get device information
- `GET /api/devices/<device_id>/location` - Get current location

### Location Tracking
- `POST /api/location/update` - Update device location (mobile agent)
- `GET /api/location/history/<device_id>` - Get location history

### Remote Access
- `POST /api/remote_access/request` - Request remote access token
- `POST /api/remote_access/revoke` - Revoke access token
- `GET /api/remote_access/logs` - View access logs

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

## Legal Compliance

This system includes:
- Consent verification mechanisms
- Activity audit trails
- Data retention policies
- User notification systems

**Consult with legal counsel before deployment in any jurisdiction.**

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or concerns, please open an issue on the repository.

---

**Remember: With great power comes great responsibility. Use ethically and legally.**
