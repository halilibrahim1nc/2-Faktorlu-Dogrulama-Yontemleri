from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import kullanici_bul, kullanici_ekle_duzenle, kisisel_test_sayisi, eposta_dogrulama_sifirla
from database import totp_secret_guncelle, totp_secret_al, olcum_loglarini_goruntule
import os
from TwoFactorAuthTypes.SMSVerification import SMSVerification
from TwoFactorAuthTypes.TOTPVerification import TOTPVerification
from TwoFactorAuthTypes.PushNotification import PushNotification
from TwoFactorAuthTypes.HardwareVerification import HardwareVerification
from TwoFactorAuthTypes.EmailVerification import EmailVerification
from TwoFactorAuthTypes.FaceRecognition import FaceRecognition
from Olcum import Olcum
import qrcode



auth_bp = Blueprint('auth', __name__)

olcum=Olcum()







## SMS Doğrulama Başlangıç 

sms_verifier = SMSVerification()
@auth_bp.route('/sms', methods=['GET', 'POST'])
def sms_verification():
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    kullanici_adi = session['kullanici_adi']
    kullanici_id = kullanici_bul(kullanici_adi)[0]
    test_sayisi=kisisel_test_sayisi(kullanici_id,"sms")[0]
    if request.method == 'POST':
        girilen_kod = request.form['sms_kodu']
        result = sms_verifier.verify_code(kullanici_adi, girilen_kod)
        if result['status'] == 'success':
            olcum.olcum_bitir(1)
            flash(result['message'], "success")
            return redirect(url_for('index'))
        else:
            olcum.olcum_bitir(0)
            flash(result['message'], "danger")
            return redirect(url_for('index'))
    else:
        olcum.set_kullanici_yontem(kullanici_id,"sms")
        sms_verifier.send_sms(kullanici_adi)
        olcum.olcum_baslat()
        flash("Sms doğrulama kodu gönderildi.", "info")
    return render_template('sms.html', test_sayisi=test_sayisi)

## SMS Doğrulama Sonu








## TOTP Google Authandicator Başlangıç 

totp_verifier = TOTPVerification()

@auth_bp.route('/totp', methods=['GET', 'POST'])
def totp_verification():
    """Kullanıcının OTP kodunu doğrular."""
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    kullanici_adi = session['kullanici_adi']
    kullanici_id = kullanici_bul(kullanici_adi)[0]
    secret = totp_secret_al(kullanici_adi)  # Veritabanından kullanıcıya özel TOTP secret al
    test_sayisi=kisisel_test_sayisi(kullanici_id,"totp")[0]
    if not secret:
        flash("TOTP kurulumu yapılmamış. Lütfen ayarlardan bir TOTP anahtarı oluşturun.", "danger")
        return redirect(url_for('auth.totp_setup'))
    
    if request.method == 'POST':
        otp = request.form['otp']
        if totp_verifier.verify_otp(secret, otp):
            olcum.olcum_bitir(1)
            flash("TOTP doğrulama başarılı!", "success")
            return redirect(url_for('index'))
        else:
            olcum.olcum_bitir(0)
            flash("TOTP doğrulama başarısız!", "danger")
    else:
        olcum.set_kullanici_yontem(kullanici_id,"totp")
    return render_template('totp.html', test_sayisi=test_sayisi)

@auth_bp.route('/totp_setup', methods=['GET', 'POST'])
def totp_setup():
    """Kullanıcı için TOTP secret anahtarı oluşturur ve gösterir."""
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    kullanici_adi = session['kullanici_adi']
    
    yeni_secret = totp_verifier.generate_secret()
    print(yeni_secret)
    totp_secret_guncelle(kullanici_adi, yeni_secret)
    

    qr_code_uri = totp_verifier.generate_qr_code(
        yeni_secret, account_name=kullanici_adi, issuer_name="2FA Test Uygulaması"
    )

    # QR kodunu oluştur ve kaydet
    qr_code_path = f"static/qr_codes/{kullanici_adi}_totp.png"
    os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)
    img = qrcode.make(qr_code_uri)
    img.save(qr_code_path)

    return render_template('totp_setup.html', totp_secret=yeni_secret, qr_code_path=qr_code_path)

## TOTP Google Authandicator Bitiş








##PUSH Bildirim Başlangıç

push_notifier = PushNotification()
@auth_bp.route('/push', methods=['GET'])
def push():
    """Push bildirim doğrulama ekranı."""
    if 'kullanici_adi' not in session:
        flash('Giriş yapmanız gerekiyor.', 'warning')
        return redirect(url_for('auth.login'))

    kullanici_adi = session['kullanici_adi']
    kullanici = kullanici_bul(kullanici_adi)
    kullanici_id=kullanici[0]
    token = kullanici[7]
    if not token:
        flash('Kayıtlı bir cihaz tokeni bulunamadı.', 'danger')
        return redirect(url_for('auth.settings'))
    result = push_notifier.send_push_notification(token, kullanici_id)
    if result['status'] == 'success':
        olcum.set_kullanici_yontem(kullanici_id,"push")
        olcum.olcum_baslat()
        flash('Telefonunuza push bildirimi gönderildi. Lütfen onaylayın.', 'success')
        return redirect(url_for('auth.push_verify'))
    else:
        flash(f"Hata: {result['message']}", 'danger')
    return render_template('push.html')



@auth_bp.route('/push_verify', methods=['GET', 'POST'])
def push_verify():
    """Push doğrulama sonucunu kontrol eder."""
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST': 
        data = request.json
        durum = data.get('durum')
        if durum == 'evet':
            olcum.olcum_bitir(1)
            return jsonify({'message': 'Doğrulama başarılı', 'redirect': url_for('index')})
        elif durum == 'hayir':
            olcum.olcum_bitir(1)      
            return jsonify({'message': 'Doğrulama başarısız', 'redirect': url_for('auth.login')})
        else:            
            olcum.olcum_bitir(0)   
            return jsonify({'error': 'Geçersiz durum'}), 400
    else:
        kullanici_id = kullanici_bul(session['kullanici_adi'])[0] 
        test_sayisi=kisisel_test_sayisi(kullanici_id,"push")[0]
    return render_template('push_verify.html', kullanici_id=kullanici_id, test_sayisi=test_sayisi)


##PUSH Bildirim Bitiş








##Donanım Anahtarı Başlangıç
 
hardware_verifier = HardwareVerification()

@auth_bp.route('/donanim_kayit', methods=['GET', 'POST'])
def donanim_kayit():
    """Donanım anahtarını kaydetme işlemi."""
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))

    kullanici_adi = session['kullanici_adi']

    if request.method == 'POST':
        result = hardware_verifier.kayit_yap(kullanici_adi)
        if result["status"] == "success":
            flash(result["message"], "success")
            return redirect(url_for('auth.kullanici_kayit')) 
        else:
            flash(result["message"], "danger")
            return redirect(url_for('auth.donanim_kayit'))

    return render_template('donanim_kayit.html')

@auth_bp.route('/donanim_dogrula', methods=['GET','POST'])
def donanim_dogrula():
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        kullanici_adi = session['kullanici_adi']
        usb_path = "D:"
        kullanici = kullanici_bul(kullanici_adi)
        sifrelenmis_anahtar = kullanici[9]
        try:
            if not os.path.exists(usb_path):
                olcum.olcum_bitir(0)
                return {"success": False, "message": "Anahtarlanmış donanım bulunamadı. Lütfen size özel anahtarlanmış donanımızı takınız.."}
            seri_numarasi = hardware_verifier.usb_seri_numarasini_al()
            cozulen_seri_numarasi = hardware_verifier.anahtari_coz(sifrelenmis_anahtar)
            if cozulen_seri_numarasi == seri_numarasi:
                olcum.olcum_bitir(1)
                return {"success": True, "message": "Donanım anahtarı doğrulama başarılı."}
            else:
                olcum.olcum_bitir(0)
                return {"danger": False, "message": "Donanım doğrulama başarısız. Seri numarası uyuşmuyor."}
        except Exception as e:
            return {"success": False, "message": str(e)}
    else:
        kullanici_adi = session['kullanici_adi']
        kullanici_id = kullanici_bul(kullanici_adi)[0]
        test_sayisi=kisisel_test_sayisi(kullanici_id,"hardware")[0]
        olcum.set_kullanici_yontem(kullanici_id,"hardware")
        olcum.olcum_baslat()

    return render_template('donanim_dogrula.html',test_sayisi=test_sayisi)

##Donanım Anahtarı Bitiş








#e-posta doğrulama

email_verifier = EmailVerification()
@auth_bp.route('/email_dogrula', methods=['GET', 'POST'])
def email_dogrula():
    """Kullanıcının e-posta doğrulama işlemi."""
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))

    kullanici_adi = session['kullanici_adi']
    kullanici = kullanici_bul(kullanici_adi)
    kullanici_eposta = kullanici[4]
    kullanici_id = kullanici[0]
    test_sayisi=kisisel_test_sayisi(kullanici_id,"email")[0]

    if request.method == 'POST':
        girilen_kod = request.form.get('kod')
        result = email_verifier.verify_code(kullanici_id, girilen_kod)
        if result['status'] == 'success':
            olcum.olcum_bitir(1)
            eposta_dogrulama_sifirla(kullanici_id)
            flash(result['message'], 'success')
            return redirect(url_for('index'))
        else:
            olcum.olcum_bitir(0)
            flash(result['message'], 'danger')
            return redirect(url_for('auth.email_dogrula',  test_sayisi= test_sayisi))
    else:
        # Doğrulama kodu gönder
        result = email_verifier.send_verification_email(kullanici_id, kullanici_eposta)
        if result['status'] == 'success':            
            olcum.set_kullanici_yontem(kullanici_id,"email")
            olcum.olcum_baslat()
            flash(result['message'], 'info')
        else:
            flash(result['message'], 'danger')
        
    return render_template('email_dogrula.html', test_sayisi= test_sayisi)

#eposta doğrulama bitiş







##Yüz Tanıma Başlangıç
face_recognizer = FaceRecognition()
@auth_bp.route('/yuz_kayit', methods=['GET', 'POST'])
def yuz_kayit():
    """Kullanıcının yüz encoding verisini kaydeder."""
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))

    kullanici_adi = session['kullanici_adi']

    if request.method == 'POST':
        gelen_resim = request.files.get('yuz_resmi')
        if not gelen_resim:
            flash("Yüz resmi alınamadı.", "danger")
            return redirect(url_for('auth.yuz_kayit'))

        result = face_recognizer.save_face_encoding(kullanici_adi, gelen_resim)
        flash(result["message"], "success" if result["status"] == "success" else "danger")
        return redirect(url_for('auth.kullanici_kayit') if result["status"] == "success" else url_for('auth.yuz_kayit'))

    return render_template('yuz_kayit.html')

@auth_bp.route('/yuz_dogrulama', methods=['GET', 'POST'])
def yuz_dogrulama():
    kullanici_adi = session['kullanici_adi']
    kullanici_id = kullanici_bul(kullanici_adi)[0]
    test_sayisi=kisisel_test_sayisi(kullanici_id,"face")[0]
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        gelen_resim = request.files.get('yuz_resmi')
        if not gelen_resim:
            return {"success": False, "message": "Yüz resmi alınamadı."}, 400
        result = face_recognizer.verify_face(kullanici_adi, gelen_resim)
        if result["status"] == "success":
            olcum.olcum_bitir(result["benzerlik"])
            return {"success": "success", "message": result["message"]}
        else:
            olcum.olcum_bitir(result["benzerlik"])
            return {"success": "error", "message": result["message"]}

    else:
        olcum.set_kullanici_yontem(kullanici_id,"face")

    return render_template('yuz_dogrulama.html', test_sayisi=test_sayisi)

##Yüz Tanıma Bitiş










@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        kullanici = kullanici_bul(kullanici_adi)
        
        if kullanici and kullanici[2] == sifre:
            # Kullanıcı bilgilerini session'a ekle
            session['kullanici_adi'] = kullanici_adi
            session['iki_faktor_yontemi'] = kullanici[5]
            return redirect(url_for('auth.iki_fa_dogrulama'))
        else:
            flash("Kullanıcı adı veya şifre hatalı!", "danger")
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))



@auth_bp.route('/kullanici_kayit', methods=['GET', 'POST'])
def kullanici_kayit():
    kullanici=None
    if request.method == 'POST':
        # Form verilerini al
        kullanici_adi = request.form.get('kullanici_adi')
        sifre = request.form.get('sifre')
        telefon = request.form.get('telefon')
        email = request.form.get('email')
        google_auth = request.form.get('google_auth')
        push_token = request.form.get('push_token')
        yontem="SMS"
        kullanici_ekle_duzenle(kullanici_adi,sifre,telefon, email, yontem, google_auth, push_token)
        session['kullanici_adi'] = kullanici_adi
        kullanici=kullanici_bul(kullanici_adi)
    else:
        if 'kullanici_adi' in session:
            kullanici=kullanici_bul(session["kullanici_adi"])
        

        
    return render_template('kullanici_kayit.html', kullanici=kullanici)      





## 2FA Yönlendirme
@auth_bp.route('/2fa', methods=['GET', 'POST'])
def iki_fa_dogrulama():
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    yontem = session.get('iki_faktor_yontemi')
    
    if yontem == 'TOTP':
        return redirect(url_for('auth.totp_verification'))
    elif yontem == 'SMS':
        return redirect(url_for('auth.sms_verification'))
    elif yontem == 'E-MAIL':
        return redirect(url_for('auth.email_dogrula'))
    elif yontem == 'PUSH':
        return redirect(url_for('auth.push'))
    elif yontem == 'YUZ':
        return redirect(url_for('auth.yuz_dogrulama'))
    elif yontem == 'DONANIM':
        return redirect(url_for('auth.donanim_dogrula'))
    elif yontem == 'PARMAK':
        return redirect(url_for('auth.parmak_izi_dogrulama'))
    else:
        flash("Geçerli bir 2FA yöntemi seçilmedi!", "danger")
        return redirect(url_for('auth.login'))
## 2FA Yönlendirme



@auth_bp.route('/olcum_log')
def olcum_log_goruntule():
    """Ölçüm loglarını listeler."""   
    loglar = olcum_loglarini_goruntule()
    return render_template('olcum_log.html', loglar=loglar)

