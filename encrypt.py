from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import base64
import os

PUBLIC_KEY = base64.b64decode(os.getenv("PUBLIC_KEY_BASE64")).decode()

def encrypt(plain_text: str) -> str:
    # Load public key from PEM
    public_key = RSA.import_key(PUBLIC_KEY)

    # Create RSA-OAEP cipher with SHA256
    cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)

    # Encrypt
    encrypted = cipher.encrypt(plain_text.encode())

    # Base64 encode
    return base64.b64encode(encrypted).decode()
