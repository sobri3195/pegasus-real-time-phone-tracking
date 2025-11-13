import os
import json
import smtplib
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from models import Alert, AlertConfig, Device, db

logger = logging.getLogger(__name__)


class NotificationManager:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@tracking.com')
        self.fcm_api_key = os.getenv('FCM_API_KEY', '')
    
    def send_alert(self, device_id, alert_type, message, severity='info'):
        device = Device.query.get(device_id)
        if not device:
            return False
        
        alert = Alert(
            device_id=device_id,
            alert_type=alert_type,
            message=message,
            severity=severity
        )
        db.session.add(alert)
        db.session.commit()
        
        alert_config = AlertConfig.query.filter_by(
            device_id=device_id,
            alert_type=alert_type,
            enabled=True
        ).first()
        
        if not alert_config:
            alert_config = AlertConfig.query.filter_by(
                device_id=device_id,
                alert_type='all',
                enabled=True
            ).first()
        
        if alert_config:
            if alert_config.email_enabled and device.owner_email:
                self.send_email(device.owner_email, alert_type, message)
            
            if alert_config.push_enabled:
                self.send_push_notification(device_id, alert_type, message)
            
            if alert_config.webhook_url:
                self.send_webhook(alert_config.webhook_url, device_id, alert_type, message)
        
        return True
    
    def send_email(self, to_email, subject, message):
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"[Tracking Alert] {subject}"
            
            body = f"""
            <html>
            <body>
                <h2>Device Tracking Alert</h2>
                <p><strong>Alert Type:</strong> {subject}</p>
                <p><strong>Message:</strong> {message}</p>
                <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <hr>
                <p><small>This is an automated message from the Phone Tracking System.</small></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_push_notification(self, device_id, title, message):
        if not self.fcm_api_key:
            logger.warning("FCM API key not configured")
            return False
        
        try:
            url = "https://fcm.googleapis.com/fcm/send"
            headers = {
                "Authorization": f"key={self.fcm_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "to": f"/topics/device_{device_id}",
                "notification": {
                    "title": title,
                    "body": message,
                    "sound": "default"
                },
                "data": {
                    "alert_type": title,
                    "device_id": device_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Push notification sent for device {device_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False
    
    def send_webhook(self, webhook_url, device_id, alert_type, message):
        try:
            payload = {
                "device_id": device_id,
                "alert_type": alert_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            logger.info(f"Webhook sent to {webhook_url}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send webhook: {str(e)}")
            return False
    
    def check_device_offline(self, device_id, last_seen):
        from datetime import timedelta
        
        offline_threshold = datetime.utcnow() - timedelta(hours=1)
        
        if last_seen and last_seen < offline_threshold:
            self.send_alert(
                device_id,
                'device_offline',
                f'Device has been offline for more than 1 hour. Last seen: {last_seen.strftime("%Y-%m-%d %H:%M:%S")} UTC',
                severity='warning'
            )
    
    def notify_geofence_event(self, device_id, geofence_name, event_type):
        message = f"Device {event_type} geofence '{geofence_name}'"
        self.send_alert(device_id, 'geofence_alert', message, severity='info')
    
    def notify_remote_access_attempt(self, device_id, ip_address):
        message = f"Remote access attempt from IP: {ip_address}"
        self.send_alert(device_id, 'remote_access_attempt', message, severity='warning')


notification_manager = NotificationManager()
