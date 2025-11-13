# API Endpoints Documentation

## Base URL
```
http://localhost:5000
```

## Overview
This document describes all available API endpoints for the Real-Time Phone Tracking System with Geofencing, Alerts, and Remote Access features.

---

## 1. Location Tracking Endpoints

### Update Location (From Mobile Agent)
**POST** `/api/update_location` or `/api/location/update`

Update device location from the mobile agent.

**Request Body:**
```json
{
  "device_id": "DEVICE_001",
  "latitude": -6.2088,
  "longitude": 106.8456,
  "source": "GPS",
  "accuracy": 5.0,
  "speed": 0,
  "battery_level": 85,
  "signal_strength": -75
}
```

**Response:**
```json
{
  "message": "Location updated successfully",
  "location": {
    "id": 123,
    "device_id": "DEVICE_001",
    "latitude": -6.2088,
    "longitude": 106.8456,
    "source": "GPS",
    "accuracy": 5.0,
    "timestamp": "2024-11-13T10:30:00"
  },
  "geofence_events": []
}
```

### Get Current Location (For Dashboard)
**GET** `/api/get_location?device_id=xxx` or `/api/devices/{device_id}/location`

Get the latest location of a device.

**Query Parameters:**
- `device_id` (required): Device identifier

**Headers:**
- `Authorization: Bearer {token}` (required)

**Response:**
```json
{
  "id": 123,
  "device_id": "DEVICE_001",
  "latitude": -6.2088,
  "longitude": 106.8456,
  "source": "GPS",
  "accuracy": 5.0,
  "battery_level": 85,
  "timestamp": "2024-11-13T10:30:00",
  "address": "Jakarta, Indonesia"
}
```

### Get Location History
**GET** `/api/location/history/{device_id}`

Get location history for a device.

**Query Parameters:**
- `limit` (optional): Number of records (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "device_id": "DEVICE_001",
  "count": 50,
  "locations": [...]
}
```

### Export Location History
**GET** `/api/location/history/{device_id}/export`

Export location history in various formats.

**Query Parameters:**
- `format` (required): csv, json, or kml
- `days` (optional): Number of days (default: 30)

**Response:** File download (CSV/JSON/KML)

---

## 2. Remote Access Endpoints (Backdoor Secure Access)

### Generate Remote Access Token
**POST** `/api/remote_access/generate` or `/api/remote_access/request`

Generate a token for remote access without dashboard login.

**Request Body:**
```json
{
  "device_id": "DEVICE_001"
}
```

**Response:**
```json
{
  "message": "Remote access token generated",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-11-14T10:30:00",
  "device_id": "DEVICE_001",
  "warning": "Token will expire in 24 hours"
}
```

**Notes:**
- Maximum 3 active tokens per device
- Requires device consent verification
- Triggers alert notification
- Rate limited: 5 requests per minute

### Get Location via Token (Backdoor Access)
**GET** `/api/remote_access/location?token=xxx`

Access location using only a token (no authentication required).

**Query Parameters:**
- `token` (required): Remote access token

**Alternative:** Use Authorization header
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "device_id": "DEVICE_001",
  "location": {
    "latitude": -6.2088,
    "longitude": 106.8456,
    "timestamp": "2024-11-13T10:30:00",
    "source": "GPS",
    "accuracy": 5.0
  },
  "device_status": {
    "is_active": true,
    "last_seen": "2024-11-13T10:30:00"
  }
}
```

### Revoke Token
**POST** `/api/remote_access/revoke`

Revoke an active token.

**Headers:**
- `Authorization: Bearer {token}` (required)

**Response:**
```json
{
  "message": "Token revoked successfully"
}
```

### Get Access Logs
**GET** `/api/remote_access/logs?device_id=xxx`

View audit logs for remote access.

**Response:**
```json
{
  "device_id": "DEVICE_001",
  "count": 10,
  "logs": [
    {
      "endpoint": "/api/remote_access/location",
      "method": "GET",
      "ip_address": "192.168.1.100",
      "timestamp": "2024-11-13T10:30:00"
    }
  ]
}
```

---

## 3. Geofencing Endpoints

### Create Geofence
**POST** `/api/geofences`

Create a virtual perimeter (100m - 10km radius).

**Request Body:**
```json
{
  "device_id": "DEVICE_001",
  "name": "Home Zone",
  "latitude": -6.2088,
  "longitude": 106.8456,
  "radius": 500,
  "notify_on_enter": true,
  "notify_on_exit": true
}
```

**Response:**
```json
{
  "message": "Geofence created successfully",
  "geofence": {
    "id": 1,
    "device_id": "DEVICE_001",
    "name": "Home Zone",
    "latitude": -6.2088,
    "longitude": 106.8456,
    "radius": 500,
    "is_active": true,
    "created_at": "2024-11-13T10:30:00"
  }
}
```

**Constraints:**
- Maximum 10 active geofences per device
- Radius: 100m - 10km
- Rate limited: 20 per hour

### Get Geofences
**GET** `/api/geofences/{device_id}`

List all geofences for a device.

**Response:**
```json
{
  "device_id": "DEVICE_001",
  "geofences": [...]
}
```

### Update Geofence
**PUT** `/api/geofences/{geofence_id}`

Update geofence settings.

**Request Body:**
```json
{
  "name": "Updated Home Zone",
  "is_active": true,
  "notify_on_enter": false
}
```

### Delete Geofence
**DELETE** `/api/geofences/{geofence_id}`

Delete a geofence.

**Response:**
```json
{
  "message": "Geofence deleted successfully"
}
```

### Get Geofence Events
**GET** `/api/geofences/{device_id}/events`

Get entry/exit event history.

**Query Parameters:**
- `limit` (optional): Number of events (default: 100)

**Response:**
```json
{
  "device_id": "DEVICE_001",
  "events": [
    {
      "id": 1,
      "geofence_id": 1,
      "event_type": "enter",
      "latitude": -6.2088,
      "longitude": 106.8456,
      "timestamp": "2024-11-13T10:30:00"
    }
  ]
}
```

---

## 4. Alert System Endpoints

### Get Alerts
**GET** `/api/alerts/{device_id}`

Get alert notifications for a device.

**Query Parameters:**
- `limit` (optional): Number of alerts (default: 50)

**Response:**
```json
{
  "device_id": "DEVICE_001",
  "alerts": [
    {
      "id": 1,
      "alert_type": "geofence_alert",
      "message": "Device enter geofence 'Home Zone'",
      "severity": "info",
      "is_read": false,
      "created_at": "2024-11-13T10:30:00"
    }
  ]
}
```

### Mark Alert as Read
**PUT** `/api/alerts/{alert_id}/read`

Mark an alert as read.

**Response:**
```json
{
  "id": 1,
  "is_read": true
}
```

### Create Alert Configuration
**POST** `/api/alerts/config`

Configure alert notifications.

**Request Body:**
```json
{
  "device_id": "DEVICE_001",
  "alert_type": "geofence_alert",
  "enabled": true,
  "email_enabled": true,
  "push_enabled": true,
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

**Alert Types:**
- `geofence_alert`: Geofence entry/exit
- `device_offline`: Device offline > 1 hour
- `remote_access_attempt`: Remote access token generated
- `gps_signal_loss`: GPS signal lost > 5 minutes
- `all`: Global alert configuration

### Get Alert Configurations
**GET** `/api/alerts/config/{device_id}`

Get alert configurations for a device.

---

## 5. Device Management Endpoints

### Register Device
**POST** `/api/devices/register`

Register a new device.

**Request Body:**
```json
{
  "owner_name": "John Doe",
  "owner_email": "john@example.com",
  "owner_phone": "+628123456789",
  "consent_verified": true
}
```

**Response:**
```json
{
  "message": "Device registered successfully",
  "device": {
    "device_id": "DEVICE_001",
    "owner_name": "John Doe",
    "consent_verified": true,
    "created_at": "2024-11-13T10:30:00"
  }
}
```

### Get Device Info
**GET** `/api/devices/{device_id}`

Get device information.

### Update Device
**PUT** `/api/devices/{device_id}`

Update device settings.

---

## 6. WebSocket Events (Real-Time Updates)

### Connect
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to server');
});
```

### Subscribe to Device Updates
```javascript
socket.emit('subscribe', { device_id: 'DEVICE_001' });

socket.on('subscribed', (data) => {
  console.log('Subscribed to device:', data.device_id);
});
```

### Receive Location Updates
```javascript
socket.on('location_update', (data) => {
  console.log('Location:', data.location);
  console.log('Geofence events:', data.geofence_events);
});
```

**Update Frequency:** Every 5 seconds (configurable)

### Request Location
```javascript
socket.emit('request_location', { device_id: 'DEVICE_001' });
```

---

## Security & Rate Limiting

### Rate Limits
- Device registration: 10 per hour
- Location updates: 120 per hour
- Remote access request: 5 per minute
- Remote access location: 30 per minute
- Geofence creation: 20 per hour
- Default: 100 per hour for other endpoints

### Authentication
- JWT tokens required for most endpoints
- Tokens expire after 24 hours
- Remote access tokens work without additional authentication

### Data Retention
- Location data automatically deleted after 30 days
- Manual delete option available
- Audit logs retained indefinitely

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "message": "Additional details (optional)"
}
```

**HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

---

## Legal Compliance

### Disclaimer
All API responses include tracking for legal compliance. The system includes:

1. **Consent Verification**: Required for device registration
2. **Email/Phone Verification**: For owner identity confirmation
3. **Audit Logging**: Complete access trail
4. **Data Retention**: Auto-delete after 30 days
5. **Access Alerts**: Notification on remote access attempts

### Required Headers
```
User-Agent: YourApp/1.0
```

### HTTPS
**Required in production environment**

---

## Dashboard Access

### Web Dashboard
```
http://localhost:5000/dashboard
```

Features:
- Live map with Leaflet.js
- Auto-update every 5 seconds via WebSocket
- Geofence visualization
- Alert notifications
- Device status indicators

---

## Example Usage

### Complete Flow Example

```bash
# 1. Register device
curl -X POST http://localhost:5000/api/devices/register \
  -H "Content-Type: application/json" \
  -d '{"owner_name": "John Doe", "consent_verified": true}'

# 2. Update location (from mobile)
curl -X POST http://localhost:5000/api/update_location \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEVICE_001",
    "latitude": -6.2088,
    "longitude": 106.8456,
    "source": "GPS",
    "accuracy": 5
  }'

# 3. Generate remote access token
curl -X POST http://localhost:5000/api/remote_access/generate \
  -H "Content-Type: application/json" \
  -d '{"device_id": "DEVICE_001"}'

# 4. Access location via token
curl "http://localhost:5000/api/remote_access/location?token=YOUR_TOKEN"

# 5. Create geofence
curl -X POST http://localhost:5000/api/geofences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEVICE_001",
    "name": "Home",
    "latitude": -6.2088,
    "longitude": 106.8456,
    "radius": 500
  }'
```

---

## Support

For issues or questions:
- Check API logs: `tracking.log`
- Review database: `tracking.db`
- Enable debug mode: `FLASK_DEBUG=True`

**Warning:** This system should only be used for authorized device tracking with proper consent.
