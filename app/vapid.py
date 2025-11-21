# app/vapid.py
from py_vapid import Vapid
import secrets

def generate_vapid_keys():
    """
    Generate VAPID keys using py-vapid (Render-safe).
    Compatible with versions that return EllipticCurvePrivateKey objects.
    """
    v = Vapid()
    v.generate_keys()

    # these RETURN PEM bytes → safe to decode
    priv = v.export_private_key().decode()
    pub = v.export_public_key().decode()

    return priv, pub


def gen_site_key():
    return secrets.token_urlsafe(32)
