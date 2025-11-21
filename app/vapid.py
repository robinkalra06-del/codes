from py_vapid import Vapid02
import secrets

def generate_vapid_keys():
    v = Vapid02()

    private_pem = v.private_key.to_pem().decode()
    public_pem = v.public_key.to_pem().decode()

    return private_pem, public_pem

def gen_site_key():
    return secrets.token_urlsafe(32)
