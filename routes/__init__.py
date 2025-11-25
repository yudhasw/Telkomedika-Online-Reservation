from .auth import auth_bp
from .main import main
from .pasien import pasien_bp

def register_routes(app):
  app.register_blueprint(auth_bp)
  app.register_blueprint(main)
  app.register_blueprint(pasien_bp)