# app/vapid.py

from py_vapid import Vapid
import secrets


# Used by your old routes
def generate_vapid_keys():
    """
    Returns (private_key_pem, public_key_pem)
    """
    v = Vapid()
    priv = v.private_key_pem().decode()
    pub = v.public_key_pem().decode()
    return priv, pub


# Used by your new routes
def generate_vapid_keys_pair():
    """
    Alias wrapper for backwards compatibility
    """
    return generate_vapid_keys()


# Generate random site key
def gen_site_key():
    return secrets.token_urlsafe(32)
