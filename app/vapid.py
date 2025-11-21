# app/vapid.py
from py_vapid import Vapid
import secrets

def generate_vapid_keys():
    """
    Universal VAPID key generation compatible with ALL py-vapid versions.
    """
    v = Vapid()

    # This method exists in ALL VERSIONS
    v.create_keys()

    # These methods ALWAYS return PEM bytes
    priv = v.get_private_key().decode()
    pub = v.get_public_key().decode()

    return priv, pub


def gen_site_key():
    return secrets.token_urlsafe(32)
