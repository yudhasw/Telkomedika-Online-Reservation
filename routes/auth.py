from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin, Pasien
from utils import admin_checker

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        nomor_hp = request.form.get('nomor_hp')
        jenis_kelamin = request.form.get('jenis_kelamin')
        tanggal_lahir = request.form.get('tanggal_lahir')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')

        if Pasien.query.filter_by(email=email).first():
          flash("Email sudah terdaftar!", "warning")
          return render_template('register.html')

        if password != confirmpassword:
          flash("Password dan Confirm Passowrd tidak sama!", "warning")
          return render_template('register.html')

        # TODO: add user creation logic here (save to DB, hash password, etc.)
        return render_template('index.html', success="Registration successful")

    return render_template('signup.html')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        if "Admin@" in email:
            user = Admin.query.filter_by(email=email).first()
            role = 'admin'
        else:
            user = Pasien.query.filter_by(email=email).first()
            role = 'user'

        if user and password:
            session['user_id'] = user.admin_id if role == 'admin' else user.pasien_id
            flash('Login berhasil!')
            return render_template('index.html')
        else:
            flash('Username atau password salah.')

    return render_template('login.html')

# check_password_hash(user.password, password)