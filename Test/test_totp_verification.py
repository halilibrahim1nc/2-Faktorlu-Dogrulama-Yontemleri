import os
from database import totp_secret_al
from TwoFactorAuthTypes.TOTPVerification import TOTPVerification

totp = TOTPVerification()

def test_totp(repeat_count=1):
    secret = totp_secret_al("test")
    if not secret:
        print("TOTP secret bulunamadı. Önce bir secret oluşturun.")
        return
    for i in range(repeat_count):
        print(i+1)
        otp = "123456"
        totp.verify_otp(secret, otp)
        

if __name__ == "__main__":
    pid = os.getpid()
    print(f"Bu işlemin PID bilgisi: {pid}")
    repeat_count = int(input("Kaç tekrar yapmak istiyorsunuz?: "))
    test_totp(repeat_count=repeat_count)
