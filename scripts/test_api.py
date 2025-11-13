#!/usr/bin/env python3
import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_register_device():
    print("\n=== Testing Device Registration ===")
    response = requests.post(f"{BASE_URL}/devices/register", json={
        "owner_name": "Test User",
        "consent_verified": True
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["device"]["device_id"]
    return None

def test_request_token(device_id):
    print("\n=== Testing Token Request ===")
    response = requests.post(f"{BASE_URL}/remote_access/request", json={
        "device_id": device_id
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_update_location(device_id):
    print("\n=== Testing Location Update ===")
    response = requests.post(f"{BASE_URL}/location/update", json={
        "device_id": device_id,
        "source": "GPS",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 5.0,
        "altitude": 10.0,
        "speed": 2.5,
        "battery_level": 85
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_location(device_id, token):
    print("\n=== Testing Get Current Location ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/devices/{device_id}/location", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_location_history(device_id, token):
    print("\n=== Testing Location History ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/location/history/{device_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    print("=== Phone Tracking System API Test ===")
    print(f"Base URL: {BASE_URL}")
    
    try:
        device_id = test_register_device()
        if not device_id:
            print("\nError: Failed to register device")
            sys.exit(1)
        
        token = test_request_token(device_id)
        if not token:
            print("\nError: Failed to get access token")
            sys.exit(1)
        
        test_update_location(device_id)
        test_get_location(device_id, token)
        test_location_history(device_id, token)
        
        print("\n=== All Tests Completed ===")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to server")
        print("Make sure the Flask server is running (python app.py)")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
