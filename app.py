from flask import Flask, redirect, render_template, session
from database import veritabani_olustur
from auth import auth_bp
from settings import settings_bp
from flask_mail import Mail


    
app = Flask(__name__)
app.secret_key = 'superguvenlik'


# Flask-Mail yapılandırması
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP sunucusu
app.config['MAIL_PORT'] = 587  # Port numarası
app.config['MAIL_USE_TLS'] = True  # TLS kullanımı
app.config['MAIL_USE_SSL'] = False  # SSL kullanılmayacak
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Gönderici e-posta adresi
app.config['MAIL_PASSWORD'] = 'your-email-password'  # E-posta şifresi
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'  # Varsayılan gönderici

mail = Mail(app)




# Veritabanını oluştur
veritabani_olustur()

app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)
#app.register_blueprint(face_auth_bp) 

@app.route('/')
def index():
    if 'kullanici_adi' in session:
        return render_template('index.html', kullanici_adi=session['kullanici_adi'])
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
    