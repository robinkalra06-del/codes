# app/vapid.py
from py_vapid import Vapid02
import secrets

def generate_vapid_keys():
    """
    Final working version for your installed py-vapid (Vapid02 with PEM export).
    """
    v = Vapid02()
    v.generate_keys()  # MUST generate keys before exporting

    # These two methods EXIST in all Vapid02 releases
    priv = v.private_key_pem().decode()
    pub = v.public_key_pem().decode()

    return priv, pub


def gen_site_key():
    return secrets.token_urlsafe(32)
