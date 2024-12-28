import os
import time
import sqlite3
from faker import Faker

fake = Faker()

conn = sqlite3.connect("../2fa_veritabani.db")
cursor = conn.cursor()

yontemler = {
    "totp_secret": "kullanicilar",
    "telefon": "kullanicilar",
    "email": "kullanicilar",
    "push_token": "kullanicilar",
    "donanim_anahtari": "kullanicilar",
    "yuz_verisi": "kullanicilar",
}

def generate_fake_data():
    return {
        "totp_secret": fake.lexify(text="?"*32, letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),

        "telefon": fake.phone_number(),

        "email": fake.email(),

        "push_token": fake.lexify(text="?"*100, letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:"),

        "donanim_anahtari": fake.password(length=256, special_chars=False, digits=True, upper_case=True, lower_case=True),

        "yuz_verisi": str([fake.random.uniform(-1, 1) for _ in range(128)])  
    }

def test_field_performance(yontem, record_counts, ilkboyut):
    for count in record_counts:
        for i in range(count - 1):
            print(f"{i+1}/{count - 1} kayıt eklendi.")
            cursor.execute(f'INSERT INTO kullanicilar ({yontem}) VALUES (?)', (generate_fake_data()[yontem],))
        conn.commit()  

        start_time = time.perf_counter()
        cursor.execute(f'INSERT INTO kullanicilar ({yontem}) VALUES (?)', (generate_fake_data()[yontem],))
        conn.commit()
        write_time = (time.perf_counter() - start_time) * 1000

       
        cursor.execute("VACUUM")
        conn.commit()
        son_boyut = os.path.getsize("../2fa_veritabani.db")
        boyut_farki = (son_boyut - ilkboyut) / 1024 / 1024  # MB 

        
        read_start_time = time.perf_counter()
        cursor.execute(f"SELECT {yontem} FROM kullanicilar")
        cursor.fetchall()
        read_time = (time.perf_counter() - read_start_time) * 1000  

        
        cursor.execute("INSERT INTO db_performance_log (yontem, records, size_diff_mb, write_time_ms, read_time_ms) VALUES (?, ?, ?, ?, ?)",
                       (yontem, count, boyut_farki, write_time, read_time))
        conn.commit()


if __name__ == "__main__":
    record_sizes = [1000, 10000, 100000]
    for yontem in yontemler:
        print(f"{yontem} alanı için test başlıyor...")
        cursor.execute("DELETE FROM kullanicilar")
        conn.commit()
        cursor.execute("VACUUM")
        ilkboyut = os.path.getsize("../2fa_veritabani.db")
        test_field_performance(yontem, record_sizes, ilkboyut)
    conn.close()


