from flask import Blueprint, render_template
from flask_login import login_required, current_user

home = Blueprint('home', __name__)

@home.route('/')
@login_required
def home_page():
  return render_template('home.html', user=current_user)