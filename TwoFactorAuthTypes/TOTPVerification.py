import pyotp

class TOTPVerification:
    def __init__(self):
        pass

    def generate_secret(self):
        return pyotp.random_base32()

    def generate_qr_code(self, secret, account_name, issuer_name):
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(account_name, issuer_name=issuer_name)

    def verify_otp(self, secret, otp):
        totp = pyotp.TOTP(secret)
        return totp.verify(otp)

    def get_current_otp(self, secret):
        totp = pyotp.TOTP(secret)
        return totp.now()
