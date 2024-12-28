import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from TwoFactorAuthTypes.EmailVerification import EmailVerification
from database import kullanici_bul

def test_email_verification():
    verifier = EmailVerification()
    kullanici_adi = "test"
    kullanici = kullanici_bul(kullanici_adi)
    kullanici_eposta = kullanici[4]
    kullanici_id = kullanici[0]

    # E-posta doğrulama kodu gönder
    print("E-posta doğrulama kodu gönderiliyor...")
    result = verifier.send_verification_email(kullanici_id, kullanici_eposta)
    print("E-posta Gönderim Sonucu:", result)

    # Kod doğrulama
    girilen_kod = input("Lütfen gelen kodu girin: ")
    verify_result = verifier.verify_code(kullanici_id, girilen_kod)
    print("Doğrulama Sonucu:", verify_result)


def test_email_verification_multi(repeat_count=1):
    verifier = EmailVerification()
    kullanici_adi = "test"
    kullanici = kullanici_bul(kullanici_adi)
    kullanici_eposta = kullanici[4]
    kullanici_id = kullanici[0]

    for i in range(repeat_count):
        print(i+1)
        result = verifier.send_verification_email(kullanici_id, kullanici_eposta)
        girilen_kod = "123456"
        verify_result = verifier.verify_code(kullanici_id, girilen_kod)
        


if __name__ == "__main__":
    pid = os.getpid()
    print(f"Bu işlemin PID bilgisi: {pid}")
    repeat_count = int(input("Kaç tekrar yapmak istiyorsunuz?: "))
    test_email_verification_multi(repeat_count=repeat_count)
    
    #test_email_verification()
