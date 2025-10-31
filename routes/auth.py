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
    username = request.form['username']
    password = request.form['password']

    if "Admin@" in username:
       user = Admin.query.filter_by(username=username).first()
       role = 'admin'
    else:
       user = Pasien.query.filter_by(username=username).first()
       role = 'user'

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.admin_id if role == 'admin' else user.pasien_id
        flash('Login berhasil!')
        return redirect(url_for('index.html'))
    else:
        flash('Username atau password salah.')

  return render_template('login.html')