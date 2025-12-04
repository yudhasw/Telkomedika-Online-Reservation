from flask import Flask, session, request, redirect, url_for
from config import Config
from models import db, Admin, Pasien
from flask_login import LoginManager
from extensions import mail
from routes import register_routes

app = Flask(__name__)

app.config.from_object(Config)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

db.init_app(app)
mail.init_app(app)

register_routes(app)

login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'auth.login_pasien'

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/admin'):
        return redirect(url_for('auth.login_admin'))
    
    return redirect(url_for('auth.login_pasien'))

@login_manager.user_loader
def load_user(user_id):
    role = session.get("role")

    if role == "admin":
        return Admin.query.get(int(user_id))
    elif role == "pasien":
        return Pasien.query.get(int(user_id))
    return None

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True)