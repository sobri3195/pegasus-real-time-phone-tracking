# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## Device Management

### Register Device
Register a new device for tracking.

**Endpoint:** `POST /api/devices/register`

**Rate Limit:** 10 requests per hour

**Request Body:**
```json
{
  "device_id": "optional-custom-id",
  "owner_name": "John Doe",
  "consent_verified": true
}
```

**Response:** `201 Created`
```json
{
  "message": "Device registered successfully",
  "device": {
    "device_id": "generated-device-id",
    "owner_name": "John Doe",
    "consent_verified": true,
    "consent_date": "2024-01-01T12:00:00",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### Get Device Information
Retrieve device details.

**Endpoint:** `GET /api/devices/<device_id>`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "device_id": "device-123",
  "owner_name": "John Doe",
  "consent_verified": true,
  "last_seen": "2024-01-01T12:30:00",
  "is_active": true
}
```

### Update Device
Update device settings.

**Endpoint:** `PUT /api/devices/<device_id>`

**Authentication:** Required

**Request Body:**
```json
{
  "is_active": false
}
```

**Response:** `200 OK`

### Get Current Location
Get the most recent location for a device.

**Endpoint:** `GET /api/devices/<device_id>/location`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": 1,
  "device_id": "device-123",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "source": "GPS",
  "accuracy": 5.0,
  "altitude": 10.0,
  "speed": 2.5,
  "battery_level": 85,
  "timestamp": "2024-01-01T12:30:00",
  "address": "123 Main St, San Francisco, CA"
}
```

---

## Location Tracking

### Update Location
Submit new location data from mobile agent.

**Endpoint:** `POST /api/location/update`

**Rate Limit:** 120 requests per hour

**Request Body (GPS):**
```json
{
  "device_id": "device-123",
  "source": "GPS",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "accuracy": 5.0,
  "altitude": 10.0,
  "speed": 2.5,
  "battery_level": 85,
  "signal_strength": -80
}
```

**Request Body (BTS):**
```json
{
  "device_id": "device-123",
  "source": "BTS",
  "cell_towers": [
    {
      "cell_id": "12345",
      "lac": "678",
      "mcc": "310",
      "mnc": "260",
      "signal_strength": -80
    },
    {
      "cell_id": "12346",
      "lac": "678",
      "mcc": "310",
      "mnc": "260",
      "signal_strength": -85
    }
  ],
  "battery_level": 85
}
```

**Response:** `201 Created`
```json
{
  "message": "Location updated successfully",
  "location": {
    "id": 1,
    "device_id": "device-123",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "source": "GPS",
    "accuracy": 5.0,
    "timestamp": "2024-01-01T12:30:00"
  }
}
```

### Get Location History
Retrieve historical location data.

**Endpoint:** `GET /api/location/history/<device_id>`

**Authentication:** Required

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 100)
- `offset` (optional): Number of records to skip (default: 0)

**Response:** `200 OK`
```json
{
  "device_id": "device-123",
  "count": 50,
  "locations": [
    {
      "id": 1,
      "latitude": 37.7749,
      "longitude": -122.4194,
      "source": "GPS",
      "accuracy": 5.0,
      "timestamp": "2024-01-01T12:30:00"
    }
  ]
}
```

---

## Remote Access

### Request Access Token
Generate a JWT token for remote access to device data.

**Endpoint:** `POST /api/remote_access/request`

**Rate Limit:** 5 requests per minute

**Request Body:**
```json
{
  "device_id": "device-123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Remote access token generated",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-01-02T12:00:00",
  "device_id": "device-123",
  "warning": "Token will expire in 24 hours"
}
```

### Revoke Access Token
Revoke an active access token.

**Endpoint:** `POST /api/remote_access/revoke`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "message": "Token revoked successfully"
}
```

### Get Access Logs
Retrieve audit logs of remote access attempts.

**Endpoint:** `GET /api/remote_access/logs?device_id=<device_id>`

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "device_id": "device-123",
  "count": 10,
  "logs": [
    {
      "id": 1,
      "session_id": 1,
      "endpoint": "/api/devices/device-123/location",
      "method": "GET",
      "ip_address": "192.168.1.100",
      "status_code": 200,
      "timestamp": "2024-01-01T12:30:00"
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid location data: GPS data must include latitude and longitude"
}
```

### 401 Unauthorized
```json
{
  "error": "No authorization token provided"
}
```

### 403 Forbidden
```json
{
  "error": "Device owner consent not verified"
}
```

### 404 Not Found
```json
{
  "error": "Device not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "5 per 1 minute"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Security Features

### Rate Limiting
- Device registration: 10 per hour
- Location updates: 120 per hour
- Remote access requests: 5 per minute
- General API: 100 per hour

### Token Expiration
- Access tokens expire after 24 hours
- Expired tokens return 401 Unauthorized
- Tokens can be manually revoked

### Data Encryption
- All sensitive data encrypted with AES-256
- HTTPS required in production
- JWT tokens signed with HS256

### Audit Logging
- All remote access attempts logged
- Logs include IP address, timestamp, and endpoint
- Logs accessible via API for review

---

## Integration Example

### Python Client
```python
import requests

BASE_URL = "http://localhost:5000/api"

# Register device
response = requests.post(f"{BASE_URL}/devices/register", json={
    "owner_name": "John Doe",
    "consent_verified": True
})
device_id = response.json()["device"]["device_id"]

# Request access token
response = requests.post(f"{BASE_URL}/remote_access/request", json={
    "device_id": device_id
})
token = response.json()["token"]

# Get current location
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"{BASE_URL}/devices/{device_id}/location",
    headers=headers
)
location = response.json()
print(f"Location: {location['latitude']}, {location['longitude']}")
```

### Mobile Agent (Kotlin)
```kotlin
// Send location update
val locationData = mapOf(
    "device_id" to deviceId,
    "source" to "GPS",
    "latitude" to 37.7749,
    "longitude" to -122.4194,
    "accuracy" to 5.0,
    "battery_level" to 85
)

api.updateLocation(locationData)
```

---

## Support

For additional help or to report issues, please refer to the main README or open an issue on the repository.
