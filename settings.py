from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from database import iki_faktor_yontemi_guncelle, kullanici_bul

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'kullanici_adi' not in session:
        flash("Önce giriş yapmalısınız!", "warning")
        return redirect(url_for('auth.login'))
    
    kullanici = kullanici_bul(session['kullanici_adi'])
    
    if request.method == 'POST':
        yeni_yontem = request.form['yontem']
        iki_faktor_yontemi_guncelle(session['kullanici_adi'], yeni_yontem)
        session['iki_faktor_yontemi'] = yeni_yontem  # Session güncelleniyor
        flash("İki faktörlü doğrulama yöntemi güncellendi!", "success")
        return redirect(url_for('settings.settings'))
    
    # Kullanıcının mevcut 2FA yöntemini veritabanından alıyoruz
    mevcut_yontem = kullanici[5] if kullanici else 'TOTP'
    
    return render_template('settings.html', mevcut_yontem=mevcut_yontem)
