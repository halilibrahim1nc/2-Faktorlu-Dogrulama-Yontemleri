from datetime import datetime
from database import olcum_log_kaydet

class Olcum:
    def __init__(self, ):
        pass

    def set_kullanici_yontem (self, kullanici_id, yontem):
        self.kullanici_id = kullanici_id
        self.yontem = yontem
        self.baslangic_zamani = datetime.now()
        self.bitis_zamani = datetime.now()

    def olcum_baslat(self):
        self.baslangic_zamani = datetime.now()

    def olcum_bitir(self, sonuc):
        self.bitis_zamani = datetime.now()
        self._olcum_verisini_kaydet( sonuc)

    def _olcum_verisini_kaydet(self, sonuc):
        olcum_log_kaydet(self.kullanici_id, self.yontem, self.baslangic_zamani, self.bitis_zamani, sonuc)