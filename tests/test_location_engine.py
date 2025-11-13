import pytest
from location_engine import LocationEngine


class TestLocationEngine:
    
    def setup_method(self):
        self.location_engine = LocationEngine()
    
    def test_process_gps_location(self):
        gps_data = {
            'source': 'GPS',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'accuracy': 5.0,
            'altitude': 10.0,
            'speed': 2.5
        }
        
        result = self.location_engine.process_location(gps_data)
        
        assert result['latitude'] == 37.7749
        assert result['longitude'] == -122.4194
        assert result['source'] == 'GPS'
        assert result['accuracy'] == 5.0
    
    def test_process_gps_location_missing_coordinates(self):
        invalid_gps_data = {
            'source': 'GPS',
            'accuracy': 5.0
        }
        
        with pytest.raises(ValueError):
            self.location_engine.process_location(invalid_gps_data)
    
    def test_estimate_distance_from_signal(self):
        signal_strength = -70
        
        distance = self.location_engine._estimate_distance_from_signal(signal_strength)
        
        assert distance > 0
        assert distance >= 50
        assert distance <= 35000
    
    def test_calculate_distance(self):
        lat1, lon1 = 37.7749, -122.4194
        lat2, lon2 = 37.7849, -122.4094
        
        distance = self.location_engine.calculate_distance(lat1, lon1, lat2, lon2)
        
        assert distance > 0
        assert isinstance(distance, float)
