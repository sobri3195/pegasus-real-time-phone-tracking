import requests
import logging
from typing import Dict, List, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import numpy as np
from scipy.optimize import least_squares
from config import Config

logger = logging.getLogger(__name__)


class LocationEngine:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="phone_tracking_system")
        self.opencellid_api_key = Config.OPENCELLID_API_KEY
        self.opencellid_url = "https://opencellid.org/cell/get"
    
    def process_location(self, location_data: Dict) -> Dict:
        source = location_data.get('source', '').upper()
        
        if source == 'GPS':
            return self._process_gps(location_data)
        elif source == 'BTS':
            return self._process_bts(location_data)
        else:
            return self._data_fusion(location_data)
    
    def _process_gps(self, data: Dict) -> Dict:
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            raise ValueError("GPS data must include latitude and longitude")
        
        return {
            'latitude': float(latitude),
            'longitude': float(longitude),
            'source': 'GPS',
            'accuracy': data.get('accuracy', 5.0),
            'altitude': data.get('altitude'),
            'speed': data.get('speed')
        }
    
    def _process_bts(self, data: Dict) -> Dict:
        cell_towers = data.get('cell_towers', [])
        
        if len(cell_towers) < 1:
            raise ValueError("BTS data requires at least one cell tower")
        
        if len(cell_towers) >= 3:
            location = self._trilateration(cell_towers)
            if location:
                return {
                    'latitude': location[0],
                    'longitude': location[1],
                    'source': 'BTS',
                    'accuracy': location[2] if len(location) > 2 else 150.0,
                    'cell_id': cell_towers[0].get('cell_id'),
                    'lac': cell_towers[0].get('lac')
                }
        
        primary_tower = cell_towers[0]
        location = self._get_tower_location(primary_tower)
        
        if location:
            return {
                'latitude': location['lat'],
                'longitude': location['lon'],
                'source': 'BTS',
                'accuracy': 200.0,
                'cell_id': primary_tower.get('cell_id'),
                'lac': primary_tower.get('lac')
            }
        
        raise ValueError("Unable to determine location from BTS data")
    
    def _get_tower_location(self, tower_info: Dict) -> Optional[Dict]:
        if not self.opencellid_api_key:
            logger.warning("OpenCellID API key not configured")
            return None
        
        params = {
            'key': self.opencellid_api_key,
            'mcc': tower_info.get('mcc'),
            'mnc': tower_info.get('mnc'),
            'lac': tower_info.get('lac'),
            'cellid': tower_info.get('cell_id'),
            'format': 'json'
        }
        
        try:
            response = requests.get(self.opencellid_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'lat': float(data['lat']),
                    'lon': float(data['lon']),
                    'range': int(data.get('range', 1000))
                }
        except Exception as e:
            logger.error(f"Error fetching tower location: {str(e)}")
        
        return None
    
    def _trilateration(self, cell_towers: List[Dict]) -> Optional[Tuple[float, float, float]]:
        tower_locations = []
        
        for tower in cell_towers[:3]:
            location = self._get_tower_location(tower)
            if location:
                signal_strength = tower.get('signal_strength', -80)
                estimated_distance = self._estimate_distance_from_signal(signal_strength)
                
                tower_locations.append({
                    'lat': location['lat'],
                    'lon': location['lon'],
                    'distance': estimated_distance
                })
        
        if len(tower_locations) < 3:
            logger.warning("Not enough tower locations for trilateration")
            return None
        
        try:
            result = self._calculate_trilateration(tower_locations)
            return result
        except Exception as e:
            logger.error(f"Trilateration calculation failed: {str(e)}")
            return None
    
    def _estimate_distance_from_signal(self, signal_strength: int) -> float:
        measured_power = -50
        n = 2.0
        
        distance = 10 ** ((measured_power - signal_strength) / (10 * n))
        
        distance_meters = distance * 1000
        distance_meters = max(50, min(distance_meters, 35000))
        
        return distance_meters
    
    def _calculate_trilateration(self, towers: List[Dict]) -> Tuple[float, float, float]:
        def equations(p):
            x, y = p
            equations_list = []
            for tower in towers:
                lat, lon = tower['lat'], tower['lon']
                distance = tower['distance']
                
                lat_m = lat * 111320
                lon_m = lon * 111320 * np.cos(np.radians(lat))
                
                calc_dist = np.sqrt((x - lon_m) ** 2 + (y - lat_m) ** 2)
                equations_list.append(calc_dist - distance)
            
            return equations_list
        
        initial_guess = [
            towers[0]['lon'] * 111320 * np.cos(np.radians(towers[0]['lat'])),
            towers[0]['lat'] * 111320
        ]
        
        result = least_squares(equations, initial_guess, method='lm')
        
        if result.success:
            x, y = result.x
            
            lat = y / 111320
            lon = x / (111320 * np.cos(np.radians(lat)))
            
            residuals = np.array(equations([x, y]))
            accuracy = float(np.sqrt(np.mean(residuals ** 2)))
            accuracy = min(accuracy, 500.0)
            
            return (lat, lon, accuracy)
        
        return None
    
    def _data_fusion(self, data: Dict) -> Dict:
        sources = []
        
        if 'gps_data' in data:
            try:
                gps_result = self._process_gps(data['gps_data'])
                sources.append(('GPS', gps_result))
            except Exception as e:
                logger.warning(f"GPS processing failed: {str(e)}")
        
        if 'bts_data' in data:
            try:
                bts_result = self._process_bts(data['bts_data'])
                sources.append(('BTS', bts_result))
            except Exception as e:
                logger.warning(f"BTS processing failed: {str(e)}")
        
        if not sources:
            raise ValueError("No valid location sources available")
        
        priority_order = ['GPS', 'BTS', 'WIFI']
        for source_type in priority_order:
            for name, result in sources:
                if name == source_type:
                    return result
        
        return sources[0][1]
    
    def get_address_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
            return location.address if location else None
        except Exception as e:
            logger.error(f"Reverse geocoding failed: {str(e)}")
            return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return geodesic((lat1, lon1), (lat2, lon2)).meters


location_engine = LocationEngine()
