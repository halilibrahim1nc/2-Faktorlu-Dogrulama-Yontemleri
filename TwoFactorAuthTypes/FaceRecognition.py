import os
import json
import face_recognition
from database import yuz_verisi_guncelle, kullanici_bul

class FaceRecognition:
    FACE_DATA_FOLDER = "face_data"
    ESIK = 60

    def __init__(self):
        os.makedirs(self.FACE_DATA_FOLDER, exist_ok=True)

    def set_ESIK(self, esik=60):
        self.ESIK=esik

    def save_face_encoding(self, kullanici_adi, gelen_resim):
        try:
            gelen_yuz = face_recognition.load_image_file(gelen_resim)
            encodingler = face_recognition.face_encodings(gelen_yuz)
            if not encodingler:
                return {"status": "error", "message": "Gönderilen resimde yüz algılanamadı."}
            face_encoding = encodingler[0].tolist()
            yuz_verisi_guncelle(kullanici_adi, json.dumps(face_encoding))
            return {"status": "success", "message": "Yüz verisi başarıyla kaydedildi."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def verify_face(self, kullanici_adi, gelen_resim):
        try:
            kullanici = kullanici_bul(kullanici_adi)
            if not kullanici or not kullanici[8]:  
                return {"status": "error", "message": "Kayıtlı yüz verisi bulunamadı."}
            yuz_verisi = json.loads(kullanici[8])
            gelen_yuz = face_recognition.load_image_file(gelen_resim)
            encodingler = face_recognition.face_encodings(gelen_yuz)
            if not encodingler:
                return {"status": "error", "message": "Gönderilen resimde yüz algılanamadı."}
            gelen_encoding = encodingler[0]
            mesafeler = face_recognition.face_distance([yuz_verisi], gelen_encoding)
            benzerlik_orani = (1 - mesafeler[0]) * 100 

            if benzerlik_orani >= self.ESIK:  
                return {"status": "success", "message": f"Eşleşme başarılı: %{benzerlik_orani:.2f}","benzerlik":benzerlik_orani}
            else:
                return {"status": "error", "message": f"Eşleşme başarısız: %{benzerlik_orani:.2f}","benzerlik":benzerlik_orani}
        except Exception as e:
            return {"status": "error", "message": str(e)}