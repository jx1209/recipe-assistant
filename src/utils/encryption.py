"""
Encryption utilities for sensitive data
Uses Fernet symmetric encryption for API keys
"""

from cryptography.fernet import Fernet
import base64
import os
from typing import Optional


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption service
        
        Args:
            encryption_key: Base64-encoded encryption key. If None, generates a new one.
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            # Generate a new key
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""
        
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt encrypted string
        
        Args:
            encrypted_text: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return ""
        
        try:
            decoded = base64.b64decode(encrypted_text.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            raise ValueError("Failed to decrypt data. Invalid encryption key or corrupted data.")
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()
    
    def get_key(self) -> str:
        """Get the current encryption key (base64-encoded)"""
        return self.key.decode()


# Singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service(encryption_key: Optional[str] = None) -> EncryptionService:
    """
    Get or create encryption service singleton
    
    Args:
        encryption_key: Optional encryption key. Uses env var if not provided.
        
    Returns:
        EncryptionService instance
    """
    global _encryption_service
    
    if _encryption_service is None:
        # Try to get key from environment or provided key
        key = encryption_key or os.getenv('ENCRYPTION_KEY')
        
        if not key:
            # Generate a new key and warn
            import logging
            logger = logging.getLogger(__name__)
            key = EncryptionService.generate_key()
            logger.warning(f"Generated new encryption key. Set ENCRYPTION_KEY environment variable to: {key}")
        
        _encryption_service = EncryptionService(key)
    
    return _encryption_service

