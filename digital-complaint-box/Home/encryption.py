"""
Encryption utilities for sensitive complaint data
"""
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.db import models
import os

class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self):
        # Use a secret key from settings or environment
        secret_key = getattr(settings, 'ENCRYPTION_KEY', 'default-secret-key-change-in-production')
        
        # Generate a key from the secret
        password = secret_key.encode()
        salt = b'salt_1234567890'  # In production, use a random salt per installation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, text):
        """Encrypt text and return base64 encoded string"""
        if not text:
            return text
        encrypted_text = self.cipher_suite.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted_text).decode()
    
    def decrypt(self, encrypted_text):
        """Decrypt base64 encoded string and return original text"""
        if not encrypted_text:
            return encrypted_text
        try:
            decoded_text = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_text = self.cipher_suite.decrypt(decoded_text)
            return decrypted_text.decode()
        except Exception as e:
            # If decryption fails, return original (might be unencrypted legacy data)
            return encrypted_text

# Global instance
encryption_manager = EncryptionManager()

class EncryptedTextField(models.TextField):
    """Custom TextField that automatically encrypts/decrypts data"""
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Decrypt when reading from database
        return encryption_manager.decrypt(value)
    
    def to_python(self, value):
        if value is None:
            return value
        # For form data, just return as-is
        return value
    
    def get_prep_value(self, value):
        if value is None:
            return value
        # Encrypt when saving to database
        return encryption_manager.encrypt(value)

class EncryptedCharField(models.CharField):
    """Custom CharField that automatically encrypts/decrypts data"""
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Decrypt when reading from database
        return encryption_manager.decrypt(value)
    
    def to_python(self, value):
        if value is None:
            return value
        # For form data, just return as-is
        return value
    
    def get_prep_value(self, value):
        if value is None:
            return value
        # Encrypt when saving to database
        return encryption_manager.encrypt(value)