from flask import Flask, session, request, redirect, url_for
from config import Config
from models import db, Admin, Pasien
from flask_login import LoginManager
from extensions import mail
from routes import register_routes
from flask_apscheduler import APScheduler
from utils.scheduler import send_reminder_job

app = Flask(__name__)

app.config.from_object(Config)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

db.init_app(app)
mail.init_app(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

register_routes(app)

login_manager = LoginManager()
login_manager.init_app(app)

@scheduler.task('cron', id='do_reminder', hour=7, minute=0)
def scheduled_task():
    send_reminder_job(app)

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
	app.run(debug=True, use_reloader=False)