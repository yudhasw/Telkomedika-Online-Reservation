from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin, Pasien

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
  return

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']

    user = Admin.query.filter_by(email=email).first()
    role = 'admin'
    if not user:
       user = Pasien.query.filter_by(email=email).first()
       role = 'user'

    if user and check_password_hash(user.password, password):
        login_user(user)
        flash('Login berhasil!', 'success')

        if role == 'admin':
            return redirect(url_for('home.html'))
        else:
            return redirect(url_for('index.html'))
    else:
        flash('Username atau password salah.', 'danger')
        return redirect(url_for('auth.login'))

  return render_template('login.html')
