import psutil
import sqlite3
from datetime import datetime


DB_PATH = "../2fa_veritabani.db"

def save_to_database(data, method, repeat_count):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for row in data:
            cursor.execute('INSERT INTO test_perform_log (timestamp, method, repeat_count, cpu_usage, ram_usage) VALUES (?, ?, ?, ?, ?)', (row['timestamp'], method, repeat_count, row['cpu'], row['ram']))
            conn.commit()
        print("Veriler veritabanına kaydedildi.")

def monitor_process(pid, method, repeat_count):
    """PID için CPU ve RAM kullanımını izler ve veritabanına kaydeder."""
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print("Geçerli bir PID bulunamadı!")
        return
    results = []
    print(f"İzleme başlatıldı. PID: {pid}")
    while True:
        try:
            cpu = process.cpu_percent(interval=1)
            memory = process.memory_info().rss / 1024 / 1024
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append({
                "timestamp": timestamp,
                "cpu": cpu,
                "ram": memory
            })
            print(f"{timestamp} | CPU: {cpu:.5f}%, RAM: {memory:.5f} MB")
        except psutil.NoSuchProcess:
            print("İzlenen işlem sonlandı, izleme durduruluyor.")
            break
    save_to_database(results, method, repeat_count)


if __name__ == "__main__":
    pid = int(input("İzlemek istediğiniz işlemin PID'sini girin: "))
    method = input("Lütfen yöntemi belirtin (örneğin: totp, sms, email): ")
    repeat_count = int(input("Kaç tekrar yapıldığını girin: "))
    monitor_process(pid, method, repeat_count)