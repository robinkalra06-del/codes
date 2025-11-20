from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generate EC key pair (P-256 Curve)
private_key = ec.generate_private_key(ec.SECP256R1())

# Export private key
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Export public key
public_key = private_key.public_key()
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# Convert to Base64 URL-safe
def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

print("PUBLIC KEY:")
print(b64url(public_bytes))

print("\nPRIVATE KEY:")
print(b64url(private_bytes))
