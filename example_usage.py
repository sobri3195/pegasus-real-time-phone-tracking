#!/usr/bin/env python3
"""
Example Usage Script
Demonstrates how to use the Real-Time Phone Tracking System API
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def main():
    print("=" * 60)
    print("  REAL-TIME PHONE TRACKING SYSTEM - USAGE EXAMPLE")
    print("=" * 60)
    
    device_id = None
    token = None
    geofence_id = None
    
    # 1. Register a device
    print_section("1. Register Device")
    response = requests.post(f"{BASE_URL}/api/devices/register", json={
        "owner_name": "Test User",
        "owner_email": "test@example.com",
        "owner_phone": "+628123456789",
        "consent_verified": True
    })
    print_response(response)
    
    if response.status_code == 201:
        device_id = response.json()['device']['device_id']
        print(f"\n✓ Device registered: {device_id}")
    else:
        print("\n✗ Failed to register device")
        return
    
    # 2. Update location (simulate mobile agent)
    print_section("2. Update Location from Mobile Agent")
    response = requests.post(f"{BASE_URL}/api/update_location", json={
        "device_id": device_id,
        "latitude": -6.2088,
        "longitude": 106.8456,
        "source": "GPS",
        "accuracy": 5.0,
        "speed": 0,
        "battery_level": 85,
        "signal_strength": -75
    })
    print_response(response)
    
    if response.status_code == 201:
        print("\n✓ Location updated successfully")
    
    # 3. Generate remote access token
    print_section("3. Generate Remote Access Token")
    response = requests.post(f"{BASE_URL}/api/remote_access/generate", json={
        "device_id": device_id
    })
    print_response(response)
    
    if response.status_code == 200:
        token = response.json()['token']
        print(f"\n✓ Token generated: {token[:50]}...")
    else:
        print("\n✗ Failed to generate token")
        return
    
    # 4. Access location via token (no auth required)
    print_section("4. Access Location via Token (Backdoor Access)")
    response = requests.get(f"{BASE_URL}/api/remote_access/location?token={token}")
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Location accessed via token successfully")
    
    # 5. Get location with device_id (alternative endpoint)
    print_section("5. Get Location via Device ID")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/get_location?device_id={device_id}", 
                          headers=headers)
    print_response(response)
    
    # 6. Create a geofence
    print_section("6. Create Geofence")
    response = requests.post(f"{BASE_URL}/api/geofences", 
        headers=headers,
        json={
            "device_id": device_id,
            "name": "Home Zone",
            "latitude": -6.2088,
            "longitude": 106.8456,
            "radius": 500,
            "notify_on_enter": True,
            "notify_on_exit": True
        }
    )
    print_response(response)
    
    if response.status_code == 201:
        geofence_id = response.json()['geofence']['id']
        print(f"\n✓ Geofence created: {geofence_id}")
    
    # 7. List geofences
    print_section("7. List Geofences")
    response = requests.get(f"{BASE_URL}/api/geofences/{device_id}", 
                          headers=headers)
    print_response(response)
    
    # 8. Update location (trigger geofence check)
    print_section("8. Update Location (Inside Geofence)")
    response = requests.post(f"{BASE_URL}/api/update_location", json={
        "device_id": device_id,
        "latitude": -6.2090,  # Slightly different
        "longitude": 106.8458,
        "source": "GPS",
        "accuracy": 5.0,
        "battery_level": 80
    })
    print_response(response)
    
    # 9. Get geofence events
    print_section("9. Get Geofence Events")
    response = requests.get(f"{BASE_URL}/api/geofences/{device_id}/events", 
                          headers=headers)
    print_response(response)
    
    # 10. Configure alert settings
    print_section("10. Configure Alert Settings")
    response = requests.post(f"{BASE_URL}/api/alerts/config",
        headers=headers,
        json={
            "device_id": device_id,
            "alert_type": "geofence_alert",
            "enabled": True,
            "email_enabled": True,
            "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK"
        }
    )
    print_response(response)
    
    # 11. Get alerts
    print_section("11. Get Alerts")
    response = requests.get(f"{BASE_URL}/api/alerts/{device_id}", 
                          headers=headers)
    print_response(response)
    
    # 12. Get location history
    print_section("12. Get Location History")
    response = requests.get(f"{BASE_URL}/api/location/history/{device_id}?limit=10", 
                          headers=headers)
    print_response(response)
    
    # 13. Export location history (CSV)
    print_section("13. Export Location History (CSV)")
    response = requests.get(
        f"{BASE_URL}/api/location/history/{device_id}/export?format=csv&days=7",
        headers=headers
    )
    if response.status_code == 200:
        print(f"✓ CSV Export successful ({len(response.content)} bytes)")
        print("\nPreview:")
        print(response.content.decode()[:200] + "...")
    
    # 14. Get remote access logs
    print_section("14. Get Remote Access Audit Logs")
    response = requests.get(f"{BASE_URL}/api/remote_access/logs?device_id={device_id}", 
                          headers=headers)
    print_response(response)
    
    # 15. Revoke token
    print_section("15. Revoke Remote Access Token")
    response = requests.post(f"{BASE_URL}/api/remote_access/revoke", 
                           headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✓ Token revoked successfully")
    
    # 16. Try to use revoked token (should fail)
    print_section("16. Try Using Revoked Token (Should Fail)")
    response = requests.get(f"{BASE_URL}/api/remote_access/location?token={token}")
    print_response(response)
    
    if response.status_code == 401:
        print("\n✓ Revoked token correctly rejected")
    
    print("\n" + "=" * 60)
    print("  EXAMPLE COMPLETED")
    print("=" * 60)
    print("\nSummary:")
    print(f"  Device ID: {device_id}")
    print(f"  Geofence ID: {geofence_id}")
    print(f"  Token Status: Revoked")
    print("\nNext steps:")
    print("  1. Open dashboard: http://localhost:5000/dashboard")
    print("  2. View API docs: http://localhost:5000")
    print("  3. Test WebSocket: See templates/dashboard.html")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server")
        print("Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
