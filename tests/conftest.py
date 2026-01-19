# tests/conftest.py
import sys
import os
import pytest
from flask import Flask, session
from flask_login import LoginManager

# pastikan root project masuk ke path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from models import db as _db, Admin, Pasien
from routes import register_routes


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    # pakai sqlite file supaya stabil (bukan in-memory)
    db_path = tmp_path_factory.mktemp("data") / "test.db"

    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        MAIL_SUPPRESS_SEND=True,
    )

    # init extensions ke app TEST (bukan app.py)
    _db.init_app(app)

    # register routes kalau mau integration test route
    register_routes(app)

    # init login manager + user_loader sesuai app.py kamu
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        role = session.get("role")
        if role == "admin":
            return Admin.query.get(int(user_id))
        elif role == "pasien":
            return Pasien.query.get(int(user_id))
        return None

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    # reset DB tiap test supaya selalu bersih (anti bentrok unique email)
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield _db
        _db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()
