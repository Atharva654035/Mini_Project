import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# WARNING: In a real app, load this from a secure location (like an environment variable), not hardcoded.
# For this project, we'll get it from an environment variable for good practice.
SECRET_KEY = os.getenv('ENCRYPTION_KEY', 'a_default_32_byte_secret_key_!!').encode('utf-8')

def encrypt_message(message):
    """Encrypts a message using AES-GCM."""
    cipher = AES.new(SECRET_KEY, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
    # We return everything needed for decryption, encoded in Base64 to be stored as text
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def decrypt_message(encrypted_message_b64):
    """Decrypts a message using AES-GCM."""
    try:
        encrypted_message = base64.b64decode(encrypted_message_b64)
        nonce = encrypted_message[:16]
        tag = encrypted_message[16:32]
        ciphertext = encrypted_message[32:]
        cipher = AES.new(SECRET_KEY, AES.MODE_GCM, nonce=nonce)
        decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_message.decode('utf-8')
    except (ValueError, KeyError):
        # If decryption fails (wrong key, corrupted data)
        return "Error: Could not decrypt message. It may be corrupted."
