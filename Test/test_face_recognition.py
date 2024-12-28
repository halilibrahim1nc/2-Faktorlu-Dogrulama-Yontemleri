import os
from TwoFactorAuthTypes.FaceRecognition import FaceRecognition


recognizer = FaceRecognition()
def test_face_recognition_multi(repeat_count=1):
    kullanici_adi = "test"
    for i in range(repeat_count):
        print(i+1)
        test_resim_path = "../test_images/test2.jpg" 
        with open(test_resim_path, "rb") as resim:
            recognizer.verify_face(kullanici_adi, resim)
            
if __name__ == "__main__":
    pid = os.getpid()
    print(f"Bu işlemin PID bilgisi: {pid}")
    repeat_count = int(input("Kaç tekrar yapmak istiyorsunuz?: "))
    test_face_recognition_multi(repeat_count=repeat_count)
