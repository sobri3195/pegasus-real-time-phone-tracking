# Android Mobile Agent

This is the Android tracking agent that collects location data and sends it to the server.

## ⚠️ Legal Requirements

Before installing this app on any device:

1. You must be the legal owner of the device
2. You must have written consent from the device owner
3. You must comply with all local privacy and tracking laws

## Features

- **GPS Location**: High-accuracy location tracking
- **BTS Data**: Cell tower information collection
- **Battery Aware**: Automatically pauses when battery is low (<15%)
- **Secure**: HTTPS communication with server
- **Consent Flow**: Built-in consent verification

## Building the App

### Prerequisites

- Android Studio Arctic Fox or newer
- Android SDK 24 or higher
- Gradle 7.0+

### Build Steps

1. Open Android Studio
2. Select "Open an Existing Project"
3. Navigate to the `mobile_agent` folder
4. Wait for Gradle sync to complete
5. Build the project: `Build > Make Project`
6. Generate APK: `Build > Build Bundle(s) / APK(s) > Build APK(s)`

### Command Line Build

```bash
cd mobile_agent
./gradlew assembleDebug
```

The APK will be generated at: `app/build/outputs/apk/debug/app-debug.apk`

## Installation

### From Android Studio

1. Connect your Android device via USB
2. Enable USB debugging on your device
3. Click the "Run" button in Android Studio

### Manual Installation

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Configuration

1. Launch the app
2. Accept the consent dialog
3. Grant all required permissions:
   - Location (Fine and Coarse)
   - Background Location
   - Phone State (for BTS data)
4. Enter your Device ID (obtained from server registration)
5. Enter your Server URL (e.g., https://your-server.com)
6. Tap "Start Tracking"

## Permissions Required

- `ACCESS_FINE_LOCATION`: For GPS coordinates
- `ACCESS_COARSE_LOCATION`: For approximate location
- `ACCESS_BACKGROUND_LOCATION`: For background tracking
- `READ_PHONE_STATE`: For cell tower information
- `INTERNET`: To send data to server
- `FOREGROUND_SERVICE`: For continuous tracking
- `WAKE_LOCK`: To keep tracking active

## How It Works

1. **Location Collection**: Uses Google Play Services FusedLocationProvider for optimal GPS data
2. **BTS Collection**: Reads cell tower info via TelephonyManager
3. **Data Transmission**: Sends location updates to server every 30 seconds via HTTPS
4. **Battery Management**: Automatically pauses tracking when battery < 15%
5. **Foreground Service**: Runs as a foreground service with persistent notification

## API Integration

The app sends POST requests to: `{SERVER_URL}/api/location/update`

Request format:
```json
{
  "device_id": "your-device-id",
  "source": "GPS",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "accuracy": 5.0,
  "altitude": 10.0,
  "speed": 0.0,
  "battery_level": 85,
  "signal_strength": -80,
  "cell_towers": [
    {
      "cell_id": "12345",
      "lac": "678",
      "mcc": "310",
      "mnc": "260",
      "signal_strength": -80
    }
  ]
}
```

## Troubleshooting

### Location Not Updating
- Ensure GPS is enabled on device
- Check that all permissions are granted
- Verify internet connectivity

### BTS Data Missing
- Ensure READ_PHONE_STATE permission is granted
- Some devices may not expose cell tower info

### High Battery Drain
- This is expected with continuous tracking
- The app automatically pauses at low battery
- Consider increasing update interval in server config

## Privacy & Security

- All data is transmitted over HTTPS
- No data is stored locally on device
- User consent is required before tracking starts
- Clear notification shown while tracking is active

## Support

For issues or questions, refer to the main project README.
