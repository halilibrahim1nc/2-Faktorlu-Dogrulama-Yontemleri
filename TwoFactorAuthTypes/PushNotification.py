import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials, db
import time

class PushNotification:
    SERVICE_ACCOUNT_FILE = "service-account.json"
    PROJECT_ID = "fir-2fapushbildirimtest"
    FCM_API_URL = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.SERVICE_ACCOUNT_FILE)
            firebase_admin.initialize_app(cred, {'databaseURL': f"https://{self.PROJECT_ID}-default-rtdb.firebaseio.com/"})

    def get_access_token(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/firebase.messaging']
        )
        credentials.refresh(Request())
        return credentials.token

    def send_push_notification(self, token, kullanici_id):
        access_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }
        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": "Giriş Onayı Gerekiyor",
                    "body": "Bir cihazdan hesabınıza giriş yapıldı. Bu sizseniz 'Evet'e basın."
                },
                "data": {
                    "kullanici_id": str(kullanici_id), 
                    "onay": "true"
                }
            }
        }
        response = requests.post(self.FCM_API_URL, headers=headers, json=message)
        if response.status_code == 200:
            self.temizle_kullanici_durumu(kullanici_id)
            return {"status": "success", "message": "Bildirim başarıyla gönderildi!"}
        else:
            return {"status": "error", "message": response.text}

    def temizle_kullanici_durumu(self, kullanici_id):
        ref = db.reference(f'oturum_dogrulama/{kullanici_id}')
        ref.delete()

    def verify_push_response(self, kullanici_id):
        ref = db.reference(f'oturum_dogrulama/{kullanici_id}')
        push_response = ref.get()
        if push_response:
            return {"status": "success", "data": push_response}
        else:
            return {"status": "error", "message": "Doğrulama cevabı bulunamadı."}

    def wait_for_push_response(self, kullanici_id, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            ref = db.reference(f'oturum_dogrulama/{kullanici_id}')
            push_response = ref.get()
            if push_response:
                if push_response.get("durum") == "evet":
                    self.temizle_kullanici_durumu(kullanici_id)
                    return {"status": "success", "message": "Doğrulama tamamlandı: Evet"}
                elif push_response.get("durum") == "hayir":
                    self.temizle_kullanici_durumu(kullanici_id)
                    return {"status": "error", "message": "Doğrulama reddedildi: Hayır"}
            time.sleep(0.5)
        self.temizle_kullanici_durumu(kullanici_id)
        return {"status": "error", "message": "Doğrulama zaman aşımına uğradı."}