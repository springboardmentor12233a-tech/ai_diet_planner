from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from app.config import settings

class EncryptionService:
    def __init__(self):
        # Generate or use existing encryption key
        if settings.ENCRYPTION_KEY:
            key = settings.ENCRYPTION_KEY.encode()
        else:
            # Generate key from secret (in production, use proper key management)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ai_nutricare_salt',
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive medical data"""
        if isinstance(data, dict):
            import json
            data = json.dumps(data)
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive medical data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_json(self, data: dict) -> str:
        """Encrypt JSON data"""
        import json
        return self.encrypt(json.dumps(data))
    
    def decrypt_json(self, encrypted_data: str) -> dict:
        """Decrypt to JSON"""
        import json
        return json.loads(self.decrypt(encrypted_data))

encryption_service = EncryptionService()
