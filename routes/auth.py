from flask import Blueprint
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
  return

@auth_bp.route("/login", methods=["GET"])
def login():
  return