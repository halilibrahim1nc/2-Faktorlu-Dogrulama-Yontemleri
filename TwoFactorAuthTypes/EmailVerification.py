import random
import time
from database import eposta_dogrulama_kodunu_veritabanina_kaydet, eposta_dogrulama_mevcut_kodu_getir
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailVerification:
    KOD_GECERLILIK_SURESI = 180  

    def __init__(self):
        pass

    def generate_verification_code(self):
        return str(random.randint(100000, 999999))

    def send_verification_email(self, kullanici_id, email):
        mevcut_kod = eposta_dogrulama_mevcut_kodu_getir(kullanici_id)
        if mevcut_kod and time.time() - float(mevcut_kod[1]) < self.KOD_GECERLILIK_SURESI:
            kalan_sure = int(self.KOD_GECERLILIK_SURESI - (time.time() - float(mevcut_kod[1])))
            return {"status": "error", "message": f"Doğrulama kodu zaten gönderildi. Kalan süre: {kalan_sure} saniye."}
        else:
            dogrulama_kodu = self.generate_verification_code()
            eposta_dogrulama_kodunu_veritabanina_kaydet(kullanici_id, dogrulama_kodu)
            if self.eposta_gonder(email, dogrulama_kodu):
                return {"status": "success", "message": "E-posta doğrulama kodu gönderildi."}
            else:
                return {"status": "error", "message": "E-posta gönderimi başarısız oldu."}

    def verify_code(self, kullanici_id, girilen_kod):
        mevcut_kod = eposta_dogrulama_mevcut_kodu_getir(kullanici_id)
        if not mevcut_kod:
            return {"status": "error", "message": "Geçerli bir doğrulama kodu bulunamadı."}
        if int(time.time() - mevcut_kod[1]) > self.KOD_GECERLILIK_SURESI:
            return {"status": "error", "message": "Doğrulama kodunun süresi doldu."}
        if int(girilen_kod) == int(mevcut_kod[0]):
            return {"status": "success", "message": "E-posta doğrulama başarılı."}
        else:
            return {"status": "error", "message": "Girilen doğrulama kodu hatalı."}

    def eposta_gonder(self, alici, dogrulama_kodu):
        try:
            mime_msg = MIMEMultipart()
            mime_msg['From'] = "halil006161@gmail.com"
            mime_msg['To'] = alici
            mime_msg['Subject'] = "2FA Giriş Doğrulama Kodu"
            mime_msg.attach(MIMEText("Doğrulama Kodunuz:"+dogrulama_kodu, 'plain'))
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  
                server.login("halil006161@gmail.com", "qqdz zzku umay vsnj")  
                server.send_message(mime_msg)  
            return True
        except Exception as e:
            print(f"E-posta gönderimi başarısız: {e}")
            return False