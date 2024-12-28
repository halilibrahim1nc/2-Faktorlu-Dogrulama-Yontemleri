
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from TwoFactorAuthTypes.SMSVerification import SMSVerification

sms_verifier = SMSVerification()

def sms_verification():
        
    # Kullanıcı bilgileri
    kullanici_adi = "test"

    # SMS gönderimi
    result = sms_verifier.send_sms(kullanici_adi)
    print("SMS Gönderim Sonucu:", result)

    # Kod doğrulama
    verification_code = input("Lütfen gelen kodu girin: ")
    result = sms_verifier.verify_code(kullanici_adi, verification_code)
    print("Doğrulama Sonucu:", result)



def sms_verification_multi(repeat_count=1):
        
    # Kullanıcı bilgileri
    kullanici_adi = "test"
    for i in range(repeat_count):
        print(i+1)
        result = sms_verifier.send_sms(kullanici_adi)
        verification_code=123456
        result = sms_verifier.verify_code(kullanici_adi, verification_code)


if __name__ == "__main__":
    pid = os.getpid()
    print(f"Bu işlemin PID bilgisi: {pid}")
    repeat_count = int(input("Kaç tekrar yapmak istiyorsunuz?: "))
    sms_verification_multi(repeat_count=repeat_count)

    
    #sms_verification()