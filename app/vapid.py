# app/vapid.py
from vapid import Vapid
import secrets

def generate_vapid_keys():
    vapid = Vapid()
    keys = vapid.create_keys()  # returns dict

    priv = keys["privateKey"]
    pub = keys["publicKey"]

    return priv, pub


def gen_site_key():
    return secrets.token_urlsafe(32)
