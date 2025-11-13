package com.tracking.agent

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var deviceIdInput: EditText
    private lateinit var serverUrlInput: EditText
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    private lateinit var statusText: TextView
    
    private val PERMISSION_REQUEST_CODE = 100
    
    private val requiredPermissions = mutableListOf(
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION,
        Manifest.permission.INTERNET
    ).apply {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            add(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            add(Manifest.permission.FOREGROUND_SERVICE)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        showConsentDialog()
        checkPermissions()
    }

    private fun initViews() {
        deviceIdInput = findViewById(R.id.deviceIdInput)
        serverUrlInput = findViewById(R.id.serverUrlInput)
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)
        statusText = findViewById(R.id.statusText)
        
        startButton.setOnClickListener { startTracking() }
        stopButton.setOnClickListener { stopTracking() }
    }

    private fun showConsentDialog() {
        AlertDialog.Builder(this)
            .setTitle("Consent Required")
            .setMessage(
                "This application will track your device location in real-time. " +
                "By proceeding, you confirm that:\n\n" +
                "1. You are the legal owner of this device\n" +
                "2. You consent to location tracking\n" +
                "3. You understand the tracking is continuous\n\n" +
                "Do you consent to location tracking?"
            )
            .setPositiveButton("I Consent") { dialog, _ ->
                dialog.dismiss()
            }
            .setNegativeButton("I Do Not Consent") { _, _ ->
                Toast.makeText(
                    this,
                    "Consent is required to use this app",
                    Toast.LENGTH_LONG
                ).show()
                finish()
            }
            .setCancelable(false)
            .show()
    }

    private fun checkPermissions() {
        val permissionsToRequest = requiredPermissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        
        if (permissionsToRequest.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                permissionsToRequest.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == PERMISSION_REQUEST_CODE) {
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            
            if (!allGranted) {
                Toast.makeText(
                    this,
                    "All permissions are required for tracking",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    private fun startTracking() {
        val deviceId = deviceIdInput.text.toString()
        val serverUrl = serverUrlInput.text.toString()
        
        if (deviceId.isEmpty() || serverUrl.isEmpty()) {
            Toast.makeText(this, "Please fill all fields", Toast.LENGTH_SHORT).show()
            return
        }
        
        val allPermissionsGranted = requiredPermissions.all {
            ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
        }
        
        if (!allPermissionsGranted) {
            Toast.makeText(
                this,
                "Please grant all permissions",
                Toast.LENGTH_SHORT
            ).show()
            checkPermissions()
            return
        }
        
        val intent = Intent(this, LocationTrackingService::class.java)
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        
        statusText.text = "Status: Tracking Active"
        Toast.makeText(this, "Tracking started", Toast.LENGTH_SHORT).show()
    }

    private fun stopTracking() {
        val intent = Intent(this, LocationTrackingService::class.java)
        stopService(intent)
        
        statusText.text = "Status: Tracking Stopped"
        Toast.makeText(this, "Tracking stopped", Toast.LENGTH_SHORT).show()
    }
}
