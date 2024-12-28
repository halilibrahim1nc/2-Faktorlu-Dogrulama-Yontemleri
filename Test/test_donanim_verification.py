import os
from TwoFactorAuthTypes.HardwareVerification import HardwareVerification

verifier = HardwareVerification()    
def test_donanim_verification_multi(repeat_count=1):
    kullanici_adi = "test"
    for i in range(repeat_count=1):
        print(i+1)
        verifier.dogrulama_yap(kullanici_adi)
    
if __name__ == "__main__":
    pid = os.getpid()
    print(f"Bu işlemin PID bilgisi: {pid}")
    repeat_count = int(input("Kaç tekrar yapmak istiyorsunuz?: "))
    test_donanim_verification_multi(repeat_count=repeat_count)