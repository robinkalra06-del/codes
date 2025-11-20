from app.vapid import generate_vapid_keys
priv, pub = generate_vapid_keys()
print('VAPID_PRIVATE=')
print(priv)
print('VAPID_PUBLIC=')
print(pub)
