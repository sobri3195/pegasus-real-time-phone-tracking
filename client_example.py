#!/usr/bin/env python3
"""
Example client library for Phone Tracking System API

This demonstrates how to interact with the tracking system from Python.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime


class TrackingClient:
    """Client for interacting with Phone Tracking System API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the tracking client.
        
        Args:
            base_url: Base URL of the tracking API
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.device_id = None
    
    def register_device(self, owner_name: str, device_id: Optional[str] = None) -> Dict:
        """
        Register a new device for tracking.
        
        Args:
            owner_name: Name of the device owner
            device_id: Optional custom device ID
        
        Returns:
            Device registration response
        """
        url = f"{self.api_url}/devices/register"
        data = {
            "owner_name": owner_name,
            "consent_verified": True
        }
        
        if device_id:
            data["device_id"] = device_id
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        self.device_id = result["device"]["device_id"]
        
        return result
    
    def request_access_token(self, device_id: str) -> str:
        """
        Request an access token for a device.
        
        Args:
            device_id: Device ID to get access for
        
        Returns:
            JWT access token
        """
        url = f"{self.api_url}/remote_access/request"
        data = {"device_id": device_id}
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        self.token = result["token"]
        self.device_id = device_id
        
        return self.token
    
    def _headers(self) -> Dict:
        """Get authorization headers"""
        if not self.token:
            raise ValueError("No access token. Call request_access_token() first.")
        
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_device_info(self, device_id: Optional[str] = None) -> Dict:
        """
        Get device information.
        
        Args:
            device_id: Device ID (uses stored device_id if not provided)
        
        Returns:
            Device information
        """
        device_id = device_id or self.device_id
        if not device_id:
            raise ValueError("No device_id provided")
        
        url = f"{self.api_url}/devices/{device_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        
        return response.json()
    
    def update_device(self, is_active: bool, device_id: Optional[str] = None) -> Dict:
        """
        Update device settings.
        
        Args:
            is_active: Whether tracking is active
            device_id: Device ID (uses stored device_id if not provided)
        
        Returns:
            Updated device information
        """
        device_id = device_id or self.device_id
        if not device_id:
            raise ValueError("No device_id provided")
        
        url = f"{self.api_url}/devices/{device_id}"
        data = {"is_active": is_active}
        
        response = requests.put(url, json=data, headers=self._headers())
        response.raise_for_status()
        
        return response.json()
    
    def get_current_location(self, device_id: Optional[str] = None) -> Dict:
        """
        Get current location of a device.
        
        Args:
            device_id: Device ID (uses stored device_id if not provided)
        
        Returns:
            Current location data
        """
        device_id = device_id or self.device_id
        if not device_id:
            raise ValueError("No device_id provided")
        
        url = f"{self.api_url}/devices/{device_id}/location"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        
        return response.json()
    
    def update_location(
        self,
        latitude: float,
        longitude: float,
        source: str = "GPS",
        accuracy: Optional[float] = None,
        altitude: Optional[float] = None,
        speed: Optional[float] = None,
        battery_level: Optional[int] = None,
        device_id: Optional[str] = None
    ) -> Dict:
        """
        Update device location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            source: Location source (GPS or BTS)
            accuracy: Location accuracy in meters
            altitude: Altitude in meters
            speed: Speed in m/s
            battery_level: Battery percentage
            device_id: Device ID (uses stored device_id if not provided)
        
        Returns:
            Location update response
        """
        device_id = device_id or self.device_id
        if not device_id:
            raise ValueError("No device_id provided")
        
        url = f"{self.api_url}/location/update"
        data = {
            "device_id": device_id,
            "source": source,
            "latitude": latitude,
            "longitude": longitude
        }
        
        if accuracy is not None:
            data["accuracy"] = accuracy
        if altitude is not None:
            data["altitude"] = altitude
        if speed is not None:
            data["speed"] = speed
        if battery_level is not None:
            data["battery_level"] = battery_level
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_location_history(
        self,
        device_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get location history for a device.
        
        Args:
            device_id: Device ID (uses stored device_id if not provided)
            limit: Maximum number of records to return
            offset: Number of records to skip
        
        Returns:
            List of location records
        """
        device_id = device_id or self.device_id
        if not device_id:
            raise ValueError("No device_id provided")
        
        url = f"{self.api_url}/location/history/{device_id}"
        params = {"limit": limit, "offset": offset}
        
        response = requests.get(url, params=params, headers=self._headers())
        response.raise_for_status()
        
        return response.json()["locations"]
    
    def revoke_token(self) -> None:
        """Revoke the current access token"""
        if not self.token:
            raise ValueError("No token to revoke")
        
        url = f"{self.api_url}/remote_access/revoke"
        response = requests.post(url, headers=self._headers())
        response.raise_for_status()
        
        self.token = None
    
    def get_access_logs(self, device_id: Optional[str] = None) -> List[Dict]:
        """
        Get access logs for a device.
        
        Args:
            device_id: Device ID (uses stored device_id if not provided)
        
        Returns:
            List of access log entries
        """
        device_id = device_id or self.device_id
        if not device_id:
            raise ValueError("No device_id provided")
        
        url = f"{self.api_url}/remote_access/logs"
        params = {"device_id": device_id}
        
        response = requests.get(url, params=params, headers=self._headers())
        response.raise_for_status()
        
        return response.json()["logs"]


def example_usage():
    """Example usage of the tracking client"""
    
    # Initialize client
    client = TrackingClient("http://localhost:5000")
    
    # Register a new device
    print("Registering device...")
    registration = client.register_device("John Doe")
    device_id = registration["device"]["device_id"]
    print(f"Device registered: {device_id}")
    
    # Request access token
    print("\nRequesting access token...")
    token = client.request_access_token(device_id)
    print(f"Token obtained: {token[:20]}...")
    
    # Update location
    print("\nUpdating location...")
    location_update = client.update_location(
        latitude=37.7749,
        longitude=-122.4194,
        accuracy=5.0,
        battery_level=85
    )
    print(f"Location updated: {location_update['message']}")
    
    # Get current location
    print("\nGetting current location...")
    current_location = client.get_current_location()
    print(f"Current location: {current_location['latitude']}, {current_location['longitude']}")
    print(f"Source: {current_location['source']}, Accuracy: {current_location['accuracy']}m")
    
    # Get location history
    print("\nGetting location history...")
    history = client.get_location_history(limit=5)
    print(f"Found {len(history)} location records")
    
    for i, loc in enumerate(history, 1):
        print(f"  {i}. {loc['latitude']}, {loc['longitude']} at {loc['timestamp']}")
    
    # Get device info
    print("\nGetting device info...")
    device_info = client.get_device_info()
    print(f"Owner: {device_info['owner_name']}")
    print(f"Active: {device_info['is_active']}")
    print(f"Last seen: {device_info['last_seen']}")
    
    # Revoke token
    print("\nRevoking access token...")
    client.revoke_token()
    print("Token revoked")


if __name__ == "__main__":
    print("=== Phone Tracking System - Client Example ===\n")
    
    try:
        example_usage()
        print("\n✓ Example completed successfully")
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
