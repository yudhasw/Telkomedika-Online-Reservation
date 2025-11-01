from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from models import Admin, Pasien
from utils import admin_checker

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
  return

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']

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