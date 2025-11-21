# app/vapid.py
import secrets
from py_vapid import Vapid02


def generate_vapid_keys():
    """
    Generate VAPID keypair using py-vapid >= 2.0
    """
    v = Vapid02()

    # IMPORTANT: Must generate keys manually
    v.generate_keys()

    private_pem = v.private_key.to_pem().decode()
    public_pem = v.public_key.to_pem().decode()

    return private_pem, public_pem


def gen_site_key():
    return secrets.token_urlsafe(32)
