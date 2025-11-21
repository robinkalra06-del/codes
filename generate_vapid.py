import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Generate private key
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Convert to raw bytes (WebPush requires this!)
public_numbers = public_key.public_numbers()
x = public_numbers.x.to_bytes(32, "big")
y = public_numbers.y.to_bytes(32, "big")

# Build uncompressed public key format
public_key_bytes = b"\x04" + x + y
private_key_bytes = private_key.private_numbers().private_value.to_bytes(32, "big")

# Base64 URL ENCODE (WebPush requirement)
def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("utf-8")

vapid_public = b64url(public_key_bytes)
vapid_private = b64url(private_key_bytes)

print("PUBLIC KEY:\n", vapid_public)
print("\nPRIVATE KEY:\n", vapid_private)
