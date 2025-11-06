from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin, Pasien

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        nama = request.form.get('name')
        email = request.form.get('email')
        nomor_hp = request.form.get('phone')
        jenis_kelamin = request.form.get('gender')
        tanggal_lahir = request.form.get('tanggal-lahir')
        password = request.form.get('password')
        confirm_password = request.form.get('conf-password')

        if Pasien.query.filter_by(email=email).first():
          flash("Email sudah terdaftar!", 'warning')
          return redirect(url_for('auth.register'))
        if password != confirm_password:
          flash("Password tidak sama!", 'warning')
          return redirect(url_for('auth.register'))
        
        password_hash = generate_password_hash(password)
        
        Pasien.create(nama, email, password_hash, nomor_hp, jenis_kelamin, tanggal_lahir)
        flash("Registrasi akun berhasil!", 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')

    user = Admin.query.filter_by(email=email).first()
    role = 'admin'
    if not user:
       user = Pasien.query.filter_by(email=email).first()
       role = 'user'

    if user and check_password_hash(user.password, password):
        login_user(user)
        flash('Login berhasil!', 'success')

        if role == 'admin':
            return redirect(url_for('main.home_page'))
        else:
            return redirect(url_for('main.home_page'))
    else:
        flash('Username atau password salah.', 'danger')
        return redirect(url_for('auth.login'))

  return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))