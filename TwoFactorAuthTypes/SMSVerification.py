import time
import random
from twilio.rest import Client
from database import kullanici_telefon_no

class SMSVerification:
    TWILIO_ACCOUNT_SID = 'ACefe36c5eee0701666c94ff14728c4197'
    TWILIO_AUTH_TOKEN = '45c5208e459c3d869b342d8b04a8e4fe'
    TWILIO_PHONE_NUMBER = '+16283000471'

    def __init__(self):
        self.twilio_client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)
        self.sms_codes = {}

    def send_sms(self, user_name):
        phone=kullanici_telefon_no(user_name)
        sms_code = str(random.randint(100000, 999999))
        self.sms_codes[user_name] = {
            'code': sms_code,
            'expires_at': time.time() + 180  
        }
        try:
            self.twilio_client.messages.create(
                body=f"Doğrulama kodunuz: {sms_code}",
                from_=self.TWILIO_PHONE_NUMBER,
                to=phone
            )
            return {"status": "success", "message": f"SMS {phone} numarasına gönderildi."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def verify_code(self, user_name, code):
        if user_name not in self.sms_codes:
            return {"status": "error", "message": "Kod bulunamadı."}
        record = self.sms_codes[user_name]
        if time.time() > record['expires_at']:
            return {"status": "error", "message": "Kodun süresi doldu."}
        if record['code'] == code:
            return {"status": "success", "message": "Kod doğrulandı."}
        else:
            return {"status": "error", "message": "Kod hatalı."}