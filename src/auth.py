import pyotp
import qrcode
import os

SECRET_FILE = "secret.txt"

def generate_secret():
    return pyotp.random_base32()

def generate_qr_code(secret, account_name):
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=account_name, issuer_name="AlarmaApp")
    qr = qrcode.make(otp_uri)
    qr.save("qrcode.png")

def verify_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def save_secret(secret):
    with open(SECRET_FILE, "w") as f:
        f.write(secret)

def load_secret():
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r") as f:
            return f.read()
    return None
