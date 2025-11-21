# app/vapid.py

import os
import secrets
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_vapid_keys_pair():
    """
    Generates a fresh VAPID private/public key pair in PEM format.
    """
    private_key = ec.generate_private_key(ec.SECP256R1())

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return private_pem, public_pem


def get_vapid_keys():
    """
    Loads VAPID keys from environment variables (Render).
    If missing, auto-generates them (optional).
    """
    priv = os.getenv("VAPID_PRIVATE_KEY")
    pub = os.getenv("VAPID_PUBLIC_KEY")

    # If not found in environment, generate new ones (optional)
    if not priv or not pub:
        priv, pub = generate_vapid_keys_pair()

    return priv, pub


def gen_site_key():
    """Generate a unique site API key"""
    return secrets.token_urlsafe(32)
