import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin, Pasien
from utils import auth_services
from extensions import admin_required, mail, Message
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/')
def homepageGuest():
    if current_user.is_authenticated:
        role = session.get("role") 

        if role == "pasien":
            return redirect(url_for('pasien.homepage'))
        elif role == "admin":
            return redirect(url_for('main.dashboard_admin'))
        
    return render_template('dashboardGuest.html', user=current_user)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        data = {
            "nama" : request.form.get('nama'),
            "email" : request.form.get('email'),
            "nomor_hp" : request.form.get('nomor_hp'),
            "jenis_kelamin" : request.form.get('jenis_kelamin'),
            "tanggal_lahir" : request.form.get('tanggal_lahir'),
            "password" : request.form.get('password'),
            "confirm_password" : request.form.get('confirm_password'),
        }

        ok, msg, cleaned = auth_services.validate_register(data)

        if not ok:
            for err in msg.values():
                if err: flash(err, 'danger')
            return render_template('register.html', old=cleaned)
        
        try:

            otp_code = str(random.randint(1000, 9999))
            
            waktu_kadaluarsa = datetime.now() + timedelta(minutes=2)
            
            session['temp_user_data'] = cleaned
            session['otp_code'] = otp_code
            session['otp_email'] = cleaned['email']
            
            session['otp_expired_at'] = waktu_kadaluarsa.timestamp()
            
            if auth_services.send_otp_email(cleaned['email'], otp_code, 'register'):
                flash('Kode OTP telah dikirim ke email Anda untuk verifikasi email.', 'info')
                return redirect(url_for('auth.verify_otp_register'))
            else:
                flash("Gagal mengirim email OTP. Periksa koneksi internet atau email Anda.", "danger")
                return render_template('register.html', old=cleaned)

        except Exception as e:
            print(f"Error Register: {e}")
            flash("Terjadi kesalahan sistem.", "danger")
            return render_template('register.html', old=cleaned)
    
    return render_template('register.html')

@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp_register():
    email = session.get('otp_email')
    expired_at = session.get('otp_expired_at')
    
    if not email or not expired_at:
        flash("Sesi tidak valid, silakan daftar ulang.", "warning")
        return redirect(url_for('auth.register'))

    if request.method == "POST":
        input_otp = request.form.get("otp_full")
        real_otp = session.get("otp_code")
        
        if input_otp == real_otp:
            user_data = session.get('temp_user_data')
 
            sekarang = datetime.now().timestamp()
        
            if sekarang > expired_at:
                session.pop('otp_code', None) 
                flash("Kode OTP telah kadaluarsa. Silakan minta kirim ulang.", "danger")
                return redirect(url_for('auth.verify_otp_register')) 
            
            if user_data:
                password_hash = generate_password_hash(user_data['password'])
                try:
                    Pasien.create(
                        nama=user_data['nama'], 
                        email=user_data['email'], 
                        password_hash=password_hash, 
                        nomor_hp=user_data['phone'], 
                        jenis_kelamin=user_data['jenis_kelamin'], 
                        tanggal_lahir=user_data['tgl_lahir'] 
                    )
                    
                    session.pop('temp_user_data', None)
                    session.pop('otp_code', None)
                    session.pop('otp_email', None)
                    
                    flash("Akun berhasil dibuat dan diverifikasi! Silakan login.", "success")
                    return redirect(url_for('auth.login_pasien'))
                    
                except Exception as e:
                    flash(f"Gagal menyimpan user ke database: {e}", "danger")
            else:
                flash("Data user hilang dari sesi. Silakan daftar ulang.", "danger")
                return redirect(url_for('auth.register'))
        else:
            flash("Kode OTP salah, silakan coba lagi.", "danger")

    return render_template(
        'verify_otp.html', 
        email=email,
        target_url=url_for('auth.verify_otp_register'),
        resend_url=url_for('auth.resend_otp_register') 
    )


@auth_bp.route("/resend-otp")
def resend_otp_register():
    email = session.get('otp_email')
    
    if email:
        new_otp = str(random.randint(1000, 9999))
       
        waktu_kadaluarsa = datetime.now() + timedelta(minutes=2)
        session['otp_expired_at'] = waktu_kadaluarsa.timestamp()
        
        session['otp_code'] = new_otp
        
        if auth_services.send_otp_email(email, new_otp, 'register'):
            flash("Kode OTP baru dikirim (Berlaku 2 menit).", "success")
        else:
            flash("Gagal mengirim ulang email.", "danger")
            
        return redirect(url_for('auth.verify_otp_register'))
    
    flash("Sesi habis.", "warning")
    return redirect(url_for('auth.register'))


@auth_bp.route("/login", methods=["GET", "POST"])
def login_pasien():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = Pasien.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        otp_code = str(random.randint(1000, 9999))
        session['login_otp'] = otp_code
        session['login_user_id'] = user.pasien_id
        session['login_role'] = 'pasien'
        session['login_email'] = user.email

        session['login_otp_expired'] = (datetime.now() + timedelta(minutes=2)).timestamp()

        session["role"] = "pasien"

        if auth_services.send_otp_email(user.email, otp_code, 'login'):
            flash('Kode OTP telah dikirim ke email Anda untuk verifikasi login.', 'info')
            return redirect(url_for('auth.verify_login_otp'))
        else:
            flash('Gagal mengirim OTP. Silakan coba lagi.', 'danger')
            return redirect(url_for('auth.login_pasien'))
    else:
        flash('Username atau password salah.', 'danger')
        return redirect(url_for('auth.login_pasien'))

  return render_template('login.html')

@auth_bp.route("/login/verify", methods=["GET", "POST"])
def verify_login_otp():
    if 'login_user_id' not in session or 'login_otp' not in session:
        return redirect(url_for('auth.login_pasien'))

    email = session.get('login_email')

    if request.method == "POST":
        input_otp = request.form.get("otp_full")
        real_otp = session.get("login_otp")
        expired_at = session.get("login_otp_expired")
 
        if datetime.now().timestamp() > expired_at:
            flash("Kode OTP kadaluarsa. Silakan login ulang.", "danger")
            return redirect(url_for('auth.login_pasien'))

        if input_otp == real_otp:
            user_id = session.get('login_user_id')
            role = session.get('login_role')
            
            if role == 'pasien':
                user = Pasien.query.get(user_id)
            else:
                user = None 

            if user:
                login_user(user)
 
                session.pop('login_otp', None)
                session.pop('login_user_id', None)
                session.pop('login_role', None)
                session.pop('login_email', None)
                session.pop('login_otp_expired', None)
                
                session["role"] = "pasien"
                flash('Login berhasil!', 'success')
                return redirect(url_for('pasien.homepage'))
            else:
                flash('User tidak ditemukan.', 'danger')
                return redirect(url_for('auth.login_pasien'))
        else:
            flash("Kode OTP salah.", "danger")

    return render_template(
        'verify_otp.html', 
        email=email,
        target_url=url_for('auth.verify_login_otp'), 
        resend_url=url_for('auth.resend_login_otp') 
    )

@auth_bp.route("/login/resend")
def resend_login_otp():
    email = session.get('login_email')
    if email:
        new_otp = str(random.randint(1000, 9999))
        session['login_otp'] = new_otp
        session['login_otp_expired'] = (datetime.now() + timedelta(minutes=2)).timestamp()
        
        auth_services.send_otp_email(email, new_otp, 'login')
        flash("Kode OTP baru dikirim.", "success")
        return redirect(url_for('auth.verify_login_otp'))
    
    return redirect(url_for('auth.login_pasien'))

@auth_bp.route('/login-admin')
@admin_required
def login_admin():
  if request.method == "POST":
    email = request.form.get('email')
    password = request.form.get('password')

    user = Admin.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
       session["role"] = "admin"
       login_user(user)
       flash("Login berhasil!", 'success')

       return redirect(url_for('main.dashboard_admin'))
    else:
       flash('Username atau password salah.', 'danger')
       return redirect(url_for('auth.login_admin'))

  return render_template('login_admin.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()

    return redirect(url_for("auth.login_pasien"))

@auth_bp.route('/login/forgot-password')
def forgot_password(user):
   
   return render_template('forgotPassword.html')
