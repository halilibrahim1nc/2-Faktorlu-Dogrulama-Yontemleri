import os
import subprocess
from cryptography.fernet import Fernet
from database import donanim_anahtari_guncelle, kullanici_bul

class HardwareVerification:
    KEY_FILE = "sifreleme_anahtari.key"

    def __init__(self):
        self.sifreleyici = Fernet(self.sifreleme_anahtarini_al())

    def sifreleme_anahtarini_al(self):
        if not os.path.exists(self.KEY_FILE):
            anahtar = Fernet.generate_key()
            with open(self.KEY_FILE, "wb") as dosya:
                dosya.write(anahtar)
        else:
            with open(self.KEY_FILE, "rb") as dosya:
                anahtar = dosya.read()
        return anahtar

    def anahtari_sifrele(self, anahtar):
        return self.sifreleyici.encrypt(anahtar.encode()).decode()

    def anahtari_coz(self, sifrelenmis_anahtar):
        return self.sifreleyici.decrypt(sifrelenmis_anahtar.encode()).decode()

    def usb_seri_numarasini_al(self):
        try:
            result = subprocess.run(
                ['wmic', 'diskdrive', 'get', 'SerialNumber'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception("Seri numarası alınamadı.")
        except FileNotFoundError:
            raise Exception("Seri numarası alınamıyor. Desteklenmeyen platform.")

    def kayit_yap(self, kullanici_adi, usb_path="D:"):
        try:
            seri_numarasi = self.usb_seri_numarasini_al()
            sifrelenmis_seri_numarasi = self.anahtari_sifrele(seri_numarasi)
            donanim_anahtari_guncelle(kullanici_adi, sifrelenmis_seri_numarasi)
            return {"status": "success", "message": "Donanım anahtarı başarıyla kaydedildi."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def dogrulama_yap(self, kullanici_adi, usb_path="D:"):
        kullanici = kullanici_bul(kullanici_adi)
        if not kullanici or not kullanici[8]:
            return {"status": "error", "message": "Doğrulama anahtarı bulunamadı. Lütfen önce kayıt olun."}
        sifrelenmis_anahtar = kullanici[8]
        try:
            seri_numarasi = self.usb_seri_numarasini_al()
            cozulen_seri_numarasi = self.anahtari_coz(sifrelenmis_anahtar)
            if cozulen_seri_numarasi == seri_numarasi:
                return {"status": "success", "message": "Donanım doğrulama başarılı."}
            else:
                return {"status": "error", "message": "Donanım doğrulama başarısız. Seri numarası uyuşmuyor."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
