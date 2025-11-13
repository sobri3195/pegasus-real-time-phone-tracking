import pytest
from datetime import datetime, timedelta
from security import SecurityManager


class TestSecurityManager:
    
    def setup_method(self):
        self.security_manager = SecurityManager()
    
    def test_generate_token(self):
        device_id = "test_device_123"
        token = self.security_manager.generate_token(device_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        device_id = "test_device_123"
        token = self.security_manager.generate_token(device_id, expires_in_hours=1)
        
        result = self.security_manager.verify_token(token)
        
        assert result['valid'] is True
        assert result['payload']['device_id'] == device_id
    
    def test_verify_invalid_token(self):
        invalid_token = "invalid.token.here"
        
        result = self.security_manager.verify_token(invalid_token)
        
        assert result['valid'] is False
        assert 'error' in result
    
    def test_encrypt_decrypt_data(self):
        original_data = "sensitive location data"
        
        encrypted = self.security_manager.encrypt_data(original_data)
        assert encrypted != original_data
        
        decrypted = self.security_manager.decrypt_data(encrypted)
        assert decrypted == original_data
    
    def test_hash_device_id(self):
        device_id = "test_device_123"
        
        hash1 = self.security_manager.hash_device_id(device_id)
        hash2 = self.security_manager.hash_device_id(device_id)
        
        assert hash1 == hash2
        assert len(hash1) == 64
    
    def test_generate_unique_device_ids(self):
        id1 = self.security_manager.generate_device_id()
        id2 = self.security_manager.generate_device_id()
        
        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0
