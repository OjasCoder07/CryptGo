from cryptography.fernet import Fernet
import base64
import hashlib

def derive_key(password: str) -> bytes:
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_data(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)

def decrypt_data(data: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(data)
