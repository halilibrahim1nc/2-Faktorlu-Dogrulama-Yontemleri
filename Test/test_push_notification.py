import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import session

from database import kullanici_bul, cihaz_tokeni_oku

from TwoFactorAuthTypes.PushNotification import PushNotification

def test_push_notification():
    push_notifier = PushNotification()

    kullanici_adi = "admin"
    kullanici_id = kullanici_bul(kullanici_adi)[0]
    token = cihaz_tokeni_oku(kullanici_id)

   
    result = push_notifier.send_push_notification(token, kullanici_id)
    print("Sonuç:", result)

    # Push doğrulama sonucu kontrol
    print("Doğrulama sonucu bekleniyor...")
    verify_result = push_notifier.wait_for_push_response(kullanici_id)
    print("Doğrulama Sonucu:", verify_result)

if __name__ == "__main__":
    test_push_notification() 



