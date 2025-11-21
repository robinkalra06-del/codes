# app/vapid.py
from py_vapid import Vapid
import secrets

def generate_vapid_keys():
    """
    Generate VAPID keys using py-vapid (Render-compatible).
    """
    v = Vapid()          # create empty instance
    v.generate_keys()    # generate new EC keypair

    # keys are bytes → decode() to strings
    priv = v.private_key.decode()
    pub = v.public_key.decode()

    return priv, pub


def gen_site_key():
    return secrets.token_urlsafe(32)
    