import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin, Pasien, db
from utils import auth_services
from extensions import mail, Message
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


# --- FUNGSI HELPER PENGIRIM EMAIL ---
def send_otp_email(target_email, otp_code):
    try:
        msg = Message(
            subject="Kode Verifikasi (OTP) - TelkoMedika",
            sender="email_anda@gmail.com", # Harus sama dengan MAIL_USERNAME di app.py
            recipients=[target_email]
        )
        msg.body = f"""
        Halo,
        
        Terima kasih telah mendaftar di TelkoMedika.
        Berikut adalah kode verifikasi (OTP) Anda:
        
        {otp_code}
        
        Kode ini bersifat rahasia. Jangan berikan kepada siapapun.
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error mengirim email: {e}")
        return False

# --- ROUTE REGISTER ---
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        # 1. Ambil Data
        data = {
            "nama" : request.form.get('nama'),
            "email" : request.form.get('email'),
            "nomor_hp" : request.form.get('nomor_hp'),
            "jenis_kelamin" : request.form.get('jenis_kelamin'),
            "tanggal_lahir" : request.form.get('tanggal_lahir'),
            "password" : request.form.get('password'),
            "confirm_password" : request.form.get('confirm_password'),
        }

        # 2. Validasi (Menggunakan utils anda)
        ok, msg, cleaned = auth_services.validate_register(data)

        if not ok:
            for err in msg.values():
                if err: flash(err, 'danger')
            return render_template('register.html', old=cleaned)
        
        try:
            # Generate OTP
            otp_code = str(random.randint(1000, 9999))
            
            # --- TAMBAHAN: LOGIKA WAKTU ---
            # Set waktu kadaluarsa 5 menit dari sekarang
            waktu_kadaluarsa = datetime.now() + timedelta(minutes=2)
            
            session['temp_user_data'] = cleaned
            session['otp_code'] = otp_code
            session['otp_email'] = cleaned['email']
            
            # Simpan waktu kadaluarsa sebagai Timestamp (float) agar bisa disimpan di session
            session['otp_expired_at'] = waktu_kadaluarsa.timestamp()
            # ------------------------------
            
            if send_otp_email(cleaned['email'], otp_code):
                flash("Registrasi berhasil! OTP berlaku selama 2 menit.", 'success')
                return redirect(url_for('auth.verify_otp'))
            else:
                flash("Gagal mengirim email OTP. Periksa koneksi internet atau email Anda.", "danger")
                return render_template('register.html', old=cleaned)

        except Exception as e:
            print(f"Error Register: {e}")
            flash("Terjadi kesalahan sistem.", "danger")
            return render_template('register.html', old=cleaned)
    
    return render_template('register.html')

# --- ROUTE VERIFIKASI OTP ---
@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    # Cek apakah ada sesi OTP yang aktif
    email = session.get('otp_email')
    expired_at = session.get('otp_expired_at')
    
    if not email or not expired_at:
        flash("Sesi tidak valid, silakan daftar ulang.", "warning")
        return redirect(url_for('auth.register'))

    if request.method == "POST":
        input_otp = request.form.get("otp_full") # Dari hidden input di frontend
        real_otp = session.get("otp_code")
        
        if input_otp == real_otp:
            # --- OTP BENAR: SIMPAN USER KE DATABASE ---
            user_data = session.get('temp_user_data')
            
            # --- CEK WAKTU DULU ---
            sekarang = datetime.now().timestamp()
        
            if sekarang > expired_at:
                # Jika waktu sekarang sudah melewati batas waktu
                session.pop('otp_code', None) # Hapus OTP agar tidak bisa dipakai lagi
                flash("Kode OTP telah kadaluarsa. Silakan minta kirim ulang.", "danger")
                return redirect(url_for('auth.verify_otp')) # Tetap di halaman OTP agar bisa klik Resend
            # ----------------------
            
            if user_data:
                try:
                    password_hash = generate_password_hash(user_data['password'])
                    new_user = Pasien(
                        nama=user_data['nama'],
                        email=user_data['email'],
                        password_hash=password_hash,
                        nomor_hp=user_data['phone'],
                        jenis_kelamin=user_data['jenis_kelamin'],
                        tanggal_lahir=user_data['tgl_lahir'],
                        # is_verified=True # Aktifkan baris ini jika ada kolom is_verified di DB
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    
                    # Bersihkan session
                    session.pop('temp_user_data', None)
                    session.pop('otp_code', None)
                    session.pop('otp_email', None)
                    
                    flash("Akun berhasil dibuat dan diverifikasi! Silakan login.", "success")
                    return redirect(url_for('auth.login_pasien'))
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f"Gagal menyimpan user ke database: {e}", "danger")
            else:
                flash("Data user hilang dari sesi. Silakan daftar ulang.", "danger")
                return redirect(url_for('auth.register'))
        else:
            flash("Kode OTP salah, silakan coba lagi.", "danger")

    return render_template('verify_otp.html', email=email)


# --- ROUTE KIRIM ULANG OTP ---
@auth_bp.route("/resend-otp")
def resend_otp():
    email = session.get('otp_email')
    
    if email:
        new_otp = str(random.randint(1000, 9999))
        
        # --- UPDATE WAKTU BARU (Reset 2 menit lagi) ---
        waktu_kadaluarsa = datetime.now() + timedelta(minutes=2)
        session['otp_expired_at'] = waktu_kadaluarsa.timestamp()
        # ---------------------------------------------
        
        session['otp_code'] = new_otp
        
        if send_otp_email(email, new_otp):
            flash("Kode OTP baru dikirim (Berlaku 2 menit).", "success")
        else:
            flash("Gagal mengirim ulang email.", "danger")
            
        return redirect(url_for('auth.verify_otp'))
    
    flash("Sesi habis.", "warning")
    return redirect(url_for('auth.register'))


def send_otp_email(target_email, otp_code):
    try:
        msg = Message(
            subject="Kode Verifikasi (OTP) - TelkoMedika",
            sender= 'yudha.sw2006@gmail.com',
            recipients=[target_email]
        )
        msg.body = f"""
        Halo,
        
        Terima kasih telah mendaftar di TelkoMedika.
        Berikut adalah kode verifikasi (OTP) Anda:
        
        {otp_code}
        
        Kode ini bersifat rahasia. Jangan berikan kepada siapapun.
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error mengirim email: {e}")
        return False


@auth_bp.route("/login", methods=["GET", "POST"])
def login_pasien():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = Pasien.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        session["role"] = "pasien"
        login_user(user)
        flash('Login berhasil!', 'success')

        return redirect(url_for('pasien.homepage'))
    else:
        flash('Username atau password salah.', 'danger')
        return redirect(url_for('auth.login_pasien'))

  return render_template('login.html')

@auth_bp.route('/login-admin')
def login_admin():
  if request.method == "POST":
    email = request.form.get('email')
    password = request.form.get('password')

    user = Admin.query.filter_by(email=email).first()
    role = 'admin'

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
