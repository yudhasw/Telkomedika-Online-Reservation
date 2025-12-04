from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin, Pasien
from utils import auth_services
from extensions import admin_required

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
                if err:
                    flash(err, 'danger')
            return render_template('register.html', old=cleaned)
        
        try:
            password_hash = generate_password_hash(cleaned['password'])

            Pasien.create(
                nama=cleaned['nama'], 
                email=cleaned['email'], 
                password_hash=password_hash, 
                nomor_hp=cleaned['phone'], 
                jenis_kelamin=cleaned['jenis_kelamin'], 
                tanggal_lahir=cleaned['tgl_lahir'] 
            )
            
            flash("Registrasi akun berhasil! Silakan login.", 'success')
            return redirect(url_for('auth.login_pasien')) 
            
        except Exception as e:
            print(f"Error Register: {e}") 
            flash("Terjadi kesalahan pada sistem database.", "danger")
            return render_template('register.html', old=cleaned)
    
    return render_template('register.html')

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
@login_required
def forgot_password(user):
   
   return render_template('forgotPassword.html')
