from py_vapid import Vapid
import secrets

def generate_vapid_keys():
    # Create fresh VAPID keypair in memory
    v = Vapid()

    # Correct attributes for Vapid02
    priv = v.private_key.decode()
    pub = v.public_key.decode()

    return priv, pub


def gen_site_key():
    return secrets.token_urlsafe(32)
