import os
import secrets
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generate_vapid_keys():
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
    """Use ENV keys if available; otherwise generate new keys."""
    priv = os.getenv("VAPID_PRIVATE_KEY")
    pub = os.getenv("VAPID_PUBLIC_KEY")

    if priv and pub:
        return priv, pub
    return generate_vapid_keys()


def gen_site_key():
    return secrets.token_urlsafe(32)
