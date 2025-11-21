# app/vapid.py
from py_vapid import Vapid02
import secrets
from cryptography.hazmat.primitives import serialization


def generate_vapid_keys():
    """
    Final universal solution for Vapid02.
    Works with versions that expose raw cryptography keys but
    do not provide any PEM export helpers.
    """
    v = Vapid02()
    v.generate_keys()  # Generates raw cryptography EC keys

    # Export private key to PEM
    priv = v.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    # Export public key to PEM
    pub = v.public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return priv, pub


def gen_site_key():
    return secrets.token_urlsafe(32)
