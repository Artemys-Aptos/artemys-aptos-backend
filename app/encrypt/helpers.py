from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.padding import PKCS7
import os
import hashlib
import base64

def generate_aes_key():
    """Generate a random AES key (256-bit) for encryption."""
    return os.urandom(32)  # 32 bytes for 256-bit AES

def encrypt_private_key_aes(aes_key: bytes, private_key: str) -> str:
    """Encrypt the private key using AES."""
    iv = os.urandom(16)  # Initialization vector (IV)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding the private key to match AES block size (128-bit)
    padder = PKCS7(128).padder()
    padded_data = padder.update(private_key.encode()) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Combine IV and encrypted data for storage
    return base64.b64encode(iv + encrypted_data).decode()

def decrypt_private_key_aes(aes_key: bytes, encrypted_private_key: str) -> str:
    """Decrypt the private key using AES."""
    encrypted_private_key = base64.b64decode(encrypted_private_key)
    iv = encrypted_private_key[:16]  # Extract IV
    encrypted_data = encrypted_private_key[16:]  # Extract encrypted data

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove padding
    unpadder = PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return decrypted_data.decode()

def hash_unique_keyword(keyword: str) -> str:
    """Hash the unique keyword using SHA-256."""
    return hashlib.sha256(keyword.encode()).hexdigest()
