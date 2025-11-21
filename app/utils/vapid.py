from py_vapid import Vapid

def generate_vapid():
    vapid = Vapid()
    vapid.generate_keys()
    return vapid.private_key, vapid.public_key