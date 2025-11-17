from flask import Flask, render_template
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, Admin, Pasien
from flask_login import LoginManager
from flask_mail import Mail
from routes import register_routes

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config["SECRET_KEY"] = SECRET_KEY
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

db.init_app(app)
register_routes(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

mail = Mail()
mail.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = Admin.query.get(int(user_id))
    if not user:
        user = Pasien.query.get(int(user_id))
    return user

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True)