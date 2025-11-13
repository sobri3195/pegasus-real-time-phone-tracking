#!/usr/bin/env python3
"""
Data Retention Cleanup Script
Automatically deletes location data older than 30 days
Run this script via cron job for automated cleanup
"""

import os
import sys
from datetime import datetime, timedelta
from app import create_app
from models import db, LocationLog, RemoteSession, AccessLog, GeofenceEvent, Alert

def cleanup_old_data(days=30, dry_run=False):
    """
    Clean up old data from the database
    
    Args:
        days (int): Number of days to retain (default: 30)
        dry_run (bool): If True, only count records without deleting
    """
    app = create_app()
    
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        print(f"Data Retention Cleanup - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Retention period: {days} days")
        print("-" * 60)
        
        location_count = LocationLog.query.filter(
            LocationLog.timestamp < cutoff_date
        ).count()
        
        expired_sessions = RemoteSession.query.filter(
            RemoteSession.expires_at < datetime.utcnow()
        ).count()
        
        old_geofence_events = GeofenceEvent.query.filter(
            GeofenceEvent.timestamp < cutoff_date
        ).count()
        
        old_alerts = Alert.query.filter(
            Alert.created_at < cutoff_date,
            Alert.is_read == True
        ).count()
        
        print(f"Location logs to delete: {location_count}")
        print(f"Expired sessions to delete: {expired_sessions}")
        print(f"Old geofence events to delete: {old_geofence_events}")
        print(f"Read alerts to delete: {old_alerts}")
        print("-" * 60)
        
        if dry_run:
            print("DRY RUN - No data deleted")
            return {
                'location_logs': location_count,
                'expired_sessions': expired_sessions,
                'geofence_events': old_geofence_events,
                'alerts': old_alerts
            }
        
        try:
            deleted_locations = LocationLog.query.filter(
                LocationLog.timestamp < cutoff_date
            ).delete()
            
            deleted_sessions = RemoteSession.query.filter(
                RemoteSession.expires_at < datetime.utcnow()
            ).delete()
            
            deleted_events = GeofenceEvent.query.filter(
                GeofenceEvent.timestamp < cutoff_date
            ).delete()
            
            deleted_alerts = Alert.query.filter(
                Alert.created_at < cutoff_date,
                Alert.is_read == True
            ).delete()
            
            db.session.commit()
            
            print(f"✓ Deleted {deleted_locations} location logs")
            print(f"✓ Deleted {deleted_sessions} expired sessions")
            print(f"✓ Deleted {deleted_events} old geofence events")
            print(f"✓ Deleted {deleted_alerts} read alerts")
            print("-" * 60)
            print("Cleanup completed successfully")
            
            return {
                'location_logs': deleted_locations,
                'expired_sessions': deleted_sessions,
                'geofence_events': deleted_events,
                'alerts': deleted_alerts
            }
        
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Cleanup failed - {str(e)}")
            sys.exit(1)


def cleanup_access_logs(days=90):
    """
    Clean up access logs older than specified days
    Access logs retained longer than location data for audit purposes
    """
    app = create_app()
    
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_logs = AccessLog.query.filter(
            AccessLog.timestamp < cutoff_date
        ).count()
        
        print(f"Access logs to delete (>{days} days): {old_logs}")
        
        if old_logs > 0:
            deleted = AccessLog.query.filter(
                AccessLog.timestamp < cutoff_date
            ).delete()
            
            db.session.commit()
            print(f"✓ Deleted {deleted} access logs")
        else:
            print("No access logs to delete")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up old tracking data')
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to retain (default: 30)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Count records without deleting'
    )
    parser.add_argument(
        '--access-logs',
        action='store_true',
        help='Also clean up old access logs (90+ days)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("REAL-TIME TRACKING SYSTEM - DATA RETENTION CLEANUP")
    print("=" * 60)
    print()
    
    results = cleanup_old_data(days=args.days, dry_run=args.dry_run)
    
    if args.access_logs:
        print()
        print("-" * 60)
        cleanup_access_logs()
    
    print()
    print("=" * 60)
    print("Cleanup script finished")
    print("=" * 60)
