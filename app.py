from flask import Flask, render_template
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, Pasien
from routes import register_routes

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config["SECRET_KEY"] = SECRET_KEY
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

db.init_app(app)

register_routes(app)

print(Pasien.__table__)             # kolom real di DB
print([a.key for a in Pasien.__mapper__.attrs])  # atribut ORM
print(Pasien.__table__.columns.keys())
print([c.name for c in Pasien.__table__.columns])

@app.route('/')
def index():
	return render_template("login.html")

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True)