from cryptography.fernet import Fernet
import os
import base64
import hashlib

class CryptoHandler:
    """Encryption and decryption handler"""
    
    def __init__(self, key=None):
        """Initialize crypto handler"""
        if key is None:
            env_key = os.environ.get('CRYPTO_KEY')
            if env_key:
                self.key = env_key.encode()
            else:
                base_key = os.environ.get('SECRET_KEY', 'quicknotify-default-key').encode()
                self.key = base64.urlsafe_b64encode(
                    hashlib.sha256(base_key).digest()
                )
        else:
            self.key = key.encode() if isinstance(key, str) else key
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, plaintext):
        """Encrypt text"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        encrypted = self.cipher.encrypt(plaintext)
        return encrypted.decode()
    
    def decrypt(self, ciphertext):
        """Decrypt text"""
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
        decrypted = self.cipher.decrypt(ciphertext)
        return decrypted.decode()