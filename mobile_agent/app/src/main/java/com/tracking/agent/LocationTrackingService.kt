package com.tracking.agent

import android.Manifest
import android.app.*
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location
import android.os.*
import android.telephony.CellInfoGsm
import android.telephony.CellInfoLte
import android.telephony.CellInfoWcdma
import android.telephony.TelephonyManager
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import com.google.android.gms.location.*
import kotlinx.coroutines.*
import java.util.concurrent.TimeUnit

class LocationTrackingService : Service() {

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private lateinit var locationCallback: LocationCallback
    private lateinit var telephonyManager: TelephonyManager
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private var deviceId: String = ""
    private var serverUrl: String = ""
    private var updateInterval: Long = 30000L // 30 seconds
    private var batteryThreshold: Int = 15
    
    companion object {
        private const val NOTIFICATION_ID = 1
        private const val CHANNEL_ID = "LocationTrackingChannel"
    }

    override fun onCreate() {
        super.onCreate()
        
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
        telephonyManager = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
        
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())
        
        setupLocationCallback()
        startLocationUpdates()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Location Tracking",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Tracking device location with owner consent"
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Location Tracking Active")
            .setContentText("Device location is being tracked with consent")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun setupLocationCallback() {
        locationCallback = object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult) {
                locationResult.lastLocation?.let { location ->
                    handleLocationUpdate(location)
                }
            }
        }
    }

    private fun startLocationUpdates() {
        if (ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            return
        }

        val locationRequest = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY,
            updateInterval
        ).apply {
            setMinUpdateIntervalMillis(updateInterval / 2)
            setMaxUpdateDelayMillis(updateInterval * 2)
        }.build()

        fusedLocationClient.requestLocationUpdates(
            locationRequest,
            locationCallback,
            Looper.getMainLooper()
        )
    }

    private fun handleLocationUpdate(location: Location) {
        if (isBatteryLow()) {
            return
        }

        val batteryLevel = getBatteryLevel()
        val cellTowerInfo = getCellTowerInfo()
        
        serviceScope.launch {
            try {
                val locationData = mapOf(
                    "device_id" to deviceId,
                    "source" to "GPS",
                    "latitude" to location.latitude,
                    "longitude" to location.longitude,
                    "accuracy" to location.accuracy.toDouble(),
                    "altitude" to if (location.hasAltitude()) location.altitude else null,
                    "speed" to if (location.hasSpeed()) location.speed.toDouble() else null,
                    "battery_level" to batteryLevel,
                    "signal_strength" to cellTowerInfo?.get("signal_strength"),
                    "cell_towers" to listOfNotNull(cellTowerInfo)
                )
                
                sendLocationToServer(locationData)
            } catch (e: Exception) {
                android.util.Log.e("LocationTracking", "Error sending location", e)
            }
        }
    }

    private fun getCellTowerInfo(): Map<String, Any?>? {
        if (ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            return null
        }

        try {
            val cellInfoList = telephonyManager.allCellInfo
            
            cellInfoList?.firstOrNull()?.let { cellInfo ->
                when (cellInfo) {
                    is CellInfoLte -> {
                        val identity = cellInfo.cellIdentity
                        val signalStrength = cellInfo.cellSignalStrength
                        
                        return mapOf(
                            "cell_id" to identity.ci.toString(),
                            "lac" to identity.tac.toString(),
                            "mcc" to identity.mccString,
                            "mnc" to identity.mncString,
                            "signal_strength" to signalStrength.dbm
                        )
                    }
                    is CellInfoGsm -> {
                        val identity = cellInfo.cellIdentity
                        val signalStrength = cellInfo.cellSignalStrength
                        
                        return mapOf(
                            "cell_id" to identity.cid.toString(),
                            "lac" to identity.lac.toString(),
                            "mcc" to identity.mccString,
                            "mnc" to identity.mncString,
                            "signal_strength" to signalStrength.dbm
                        )
                    }
                    is CellInfoWcdma -> {
                        val identity = cellInfo.cellIdentity
                        val signalStrength = cellInfo.cellSignalStrength
                        
                        return mapOf(
                            "cell_id" to identity.cid.toString(),
                            "lac" to identity.lac.toString(),
                            "mcc" to identity.mccString,
                            "mnc" to identity.mncString,
                            "signal_strength" to signalStrength.dbm
                        )
                    }
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("LocationTracking", "Error getting cell info", e)
        }
        
        return null
    }

    private fun isBatteryLow(): Boolean {
        val batteryLevel = getBatteryLevel()
        return batteryLevel < batteryThreshold
    }

    private fun getBatteryLevel(): Int {
        val batteryManager = getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        return batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
    }

    private suspend fun sendLocationToServer(locationData: Map<String, Any?>) {
        // Implementation would use Retrofit to send data to server
        // For now, this is a placeholder
        withContext(Dispatchers.IO) {
            // ApiClient.locationApi.updateLocation(locationData)
            android.util.Log.d("LocationTracking", "Sending location: $locationData")
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        fusedLocationClient.removeLocationUpdates(locationCallback)
        serviceScope.cancel()
    }
}
