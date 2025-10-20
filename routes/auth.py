from flask import Blueprint
from flask_login import login_user, logout_user, login_required

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["GET", "POST"])
def register():
  return