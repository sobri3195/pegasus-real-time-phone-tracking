import math
from datetime import datetime
from models import Geofence, GeofenceEvent, db


class GeofenceManager:
    def __init__(self):
        self.device_states = {}
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def check_geofences(self, device_id, latitude, longitude):
        geofences = Geofence.query.filter_by(device_id=device_id, is_active=True).all()
        events = []
        
        if device_id not in self.device_states:
            self.device_states[device_id] = {}
        
        for geofence in geofences:
            distance = self.calculate_distance(
                latitude, longitude,
                geofence.latitude, geofence.longitude
            )
            
            is_inside = distance <= geofence.radius
            was_inside = self.device_states[device_id].get(geofence.id, False)
            
            event = None
            if is_inside and not was_inside and geofence.notify_on_enter:
                event = GeofenceEvent(
                    geofence_id=geofence.id,
                    device_id=device_id,
                    event_type='enter',
                    latitude=latitude,
                    longitude=longitude
                )
                events.append(event)
            elif not is_inside and was_inside and geofence.notify_on_exit:
                event = GeofenceEvent(
                    geofence_id=geofence.id,
                    device_id=device_id,
                    event_type='exit',
                    latitude=latitude,
                    longitude=longitude
                )
                events.append(event)
            
            self.device_states[device_id][geofence.id] = is_inside
            
            if event:
                db.session.add(event)
        
        if events:
            db.session.commit()
        
        return events
    
    def create_geofence(self, device_id, name, latitude, longitude, radius, 
                       notify_on_enter=True, notify_on_exit=True):
        if radius < 100 or radius > 10000:
            raise ValueError("Radius must be between 100m and 10km")
        
        geofence = Geofence(
            device_id=device_id,
            name=name,
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            notify_on_enter=notify_on_enter,
            notify_on_exit=notify_on_exit
        )
        
        db.session.add(geofence)
        db.session.commit()
        
        return geofence
    
    def get_geofences(self, device_id):
        return Geofence.query.filter_by(device_id=device_id).all()
    
    def update_geofence(self, geofence_id, **kwargs):
        geofence = Geofence.query.get(geofence_id)
        if not geofence:
            return None
        
        for key, value in kwargs.items():
            if hasattr(geofence, key):
                setattr(geofence, key, value)
        
        db.session.commit()
        return geofence
    
    def delete_geofence(self, geofence_id):
        geofence = Geofence.query.get(geofence_id)
        if geofence:
            db.session.delete(geofence)
            db.session.commit()
            return True
        return False


geofence_manager = GeofenceManager()
