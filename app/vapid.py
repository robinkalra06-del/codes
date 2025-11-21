# app/vapid.py

from pywebpush import generate_vapid_keys

def generate_vapid_keys_pair():
    keys = generate_vapid_keys()
    private_key = keys["privateKey"]
    public_key = keys["publicKey"]
    return private_key, public_key
