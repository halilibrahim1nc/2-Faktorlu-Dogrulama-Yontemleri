import sqlite3
import time
from contextlib import contextmanager
from config import DATABASE_PATH


@contextmanager
def get_db_connection():
    """ Veritabanı bağlantısını yöneten context manager. """
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()


def veritabani_olustur():
    """Veritabanını oluşturur."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE,
            sifre TEXT,
            telefon TEXT,
            email TEXT,
            iki_faktor_yontemi TEXT DEFAULT 'TOTP'
        )
    ''')
    
    conn.commit()
    conn.close()

def kullanici_ekle_duzenle(kullanici_adi, sifre, telefon, email, yontem, totp_secret, push_token):
    """Yeni kullanıcı ekler."""
    kul=kullanici_bul(kullanici_adi)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if kul:
            cursor.execute('UPDATE kullanicilar SET kullanici_adi=? , sifre=?, telefon=?, email=?, iki_faktor_yontemi=?, totp_secret=?, push_token=? WHERE id=?', (kullanici_adi, sifre, "+90"+telefon, email, yontem, totp_secret, push_token, kul[0]))
        else:
            cursor.execute('''
                INSERT INTO kullanicilar (kullanici_adi, sifre, telefon, email, iki_faktor_yontemi, totp_secret, push_token)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (kullanici_adi, sifre, "+90"+telefon, email, yontem, totp_secret, push_token))
        conn.commit()

def kullanici_bul(kullanici_adi):
    """Kullanıcıyı kullanıcı adına göre bulur."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM kullanicilar WHERE kullanici_adi = ?', (kullanici_adi,))
        return cursor.fetchone()

def kullanici_telefon_no(kullanici_adi):
    """Kullanıcıyı kullanıcı adına göre bulur."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT telefon FROM kullanicilar WHERE kullanici_adi = ?', (kullanici_adi,))
        return cursor.fetchone()

def cihaz_tokeni_oku(kullanici_id):
    """Belirtilen kullanıcı ID'sine ait cihaz tokenini veritabanından oku."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT push_token FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
        row = cursor.fetchone()
        return row[0] if row else None

def iki_faktor_yontemi_guncelle(kullanici_adi, yontem):
    """Kullanıcının iki faktörlü doğrulama yöntemini günceller."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE kullanicilar SET iki_faktor_yontemi = ? WHERE kullanici_adi = ?', (yontem, kullanici_adi))
        conn.commit()

def totp_secret_guncelle(kullanici_adi, secret):
    """Bir kullanıcının TOTP secret anahtarını günceller."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE kullanicilar SET totp_secret = ? WHERE kullanici_adi = ?', (secret, kullanici_adi))
        conn.commit()

def totp_secret_al(kullanici_adi):
    """Bir kullanıcının TOTP secret anahtarını döner."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT totp_secret FROM kullanicilar WHERE kullanici_adi = ?', (kullanici_adi,))
        secret = cursor.fetchone()
        return secret[0] if secret else None

def donanim_anahtari_guncelle(kullanici_adi, anahtar_verisi):
    """Kullanıcının donanım anahtarını günceller."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE kullanicilar SET donanim_anahtari = ? WHERE kullanici_adi = ?', (anahtar_verisi, kullanici_adi))
        conn.commit()

def yuz_verisi_guncelle(kullanici_adi, yuz_verisi):
    """Bir kullanıcının yüz encoding bilgisini günceller."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE kullanicilar SET yuz_verisi = ? WHERE kullanici_adi = ?', (yuz_verisi, kullanici_adi))
        conn.commit()

def eposta_dogrulama_kodunu_veritabanina_kaydet(kullanici_id, kod):
    """Doğrulama kodunu veritabanına kaydeder."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE kullanicilar SET email_kod = ?, email_olusturma_zamani = ? WHERE id = ?;', (kod, time.time(), kullanici_id))
        conn.commit()   

def eposta_dogrulama_mevcut_kodu_getir(kullanici_id):
    """Kullanıcıyı kullanıcı id'sine göre bulur."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT email_kod, email_olusturma_zamani FROM kullanicilar WHERE id = ?;', (kullanici_id,))
        sonuc = cursor.fetchone()
        return sonuc

def eposta_dogrulama_sifirla(kullanici_id):
    """Kullanıcıyı kullanıcı id'sine göre bulur."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE kullanicilar SET email_kod = NULL, email_olusturma_zamani = ? WHERE id = ?;', (float(0), kullanici_id))
        conn.commit() 

def parmak_izi_verilerini_kaydet(kullanici_id, karakteristik):
    """Kullanıcının parmak izi verilerini kaydeder."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO parmak_izi (kullanici_id, karakteristik) VALUES (?, ?)', (kullanici_id, str(karakteristik)))
        conn.commit()   

def olcum_log_kaydet(kullanici_id, yontem, baslangic_zamani, bitis_zamani, sonuc):
    """Ölçüm verisini log tablosuna kaydeder."""
    sure_ms = int((bitis_zamani - baslangic_zamani).total_seconds() * 1000)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO olcum_log (kullanici_id, yontem, baslangic_zamani, bitis_zamani, sure_ms, sonuc) VALUES (?, ?, ?, ?, ?, ?)', (kullanici_id, yontem, baslangic_zamani, bitis_zamani, sure_ms, sonuc))
        conn.commit()
    
def olcum_loglarini_goruntule():
    """Ölçüm loglarını listeler."""
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM olcum_log")
        loglar = cursor.fetchall()
        return loglar

def kisisel_test_sayisi(kullanici_id,yontem):
     with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM olcum_log WHERE kullanici_id = ? AND yontem = ?;', (kullanici_id,yontem))
        sonuc = cursor.fetchone()
        return sonuc
