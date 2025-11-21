# app/vapid.py

import secrets
from py_vapid import Vapid
import base64


def _convert_public_to_base64(public_key_bytes: bytes) -> str:
    """
    Converts uncompressed EC public key (65 bytes, starting with 0x04)
    into Browser-Compatible Base64 URL-Safe string.

    Required for:
        - pushManager.subscribe()
        - VAPID public key for the client
    """
    return base64.urlsafe_b64encode(public_key_bytes).rstrip(b"=").decode("utf-8")


def generate_vapid_keys():
    """
    Generates a VAPID key pair.
    Returns:
        private_pem (str)  → Save on server
        public_pem  (str)  → Save on server
        public_base64 (str) → For browser PushManager.subscribe()
    """
    v = Vapid()

    private_pem = v.private_key_pem().decode()
    public_pem = v.public_key_pem().decode()

    # Public key bytes (raw EC 65-byte format)
    public_key_bytes = v.public_key()

    # Convert to browser-compatible Base64 URL-safe key
    public_base64 = _convert_public_to_base64(public_key_bytes)

    return private_pem, public_pem, public_base64


def gen_site_key():
    """
    Generates a unique website key for each user domain.
    Returned string is safe for URLs and headers.
    """
    return secrets.token_urlsafe(32)
