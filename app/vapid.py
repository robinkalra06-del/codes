# app/vapid.py
from py_vapid import Vapid
import secrets

def generate_vapid_keys():
    # returns (private_pem, public_pem)
    v = Vapid()
    priv = v.private_key_pem().decode()
    pub = v.public_key_pem().decode()
    return priv, pub

def gen_site_key():
    return secrets.token_urlsafe(32)
