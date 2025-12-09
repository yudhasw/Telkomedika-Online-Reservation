from .auth import auth_bp
from .pasien import pasien_bp
from .admin import admin_bp

def register_routes(app):
  app.register_blueprint(auth_bp)
  app.register_blueprint(pasien_bp)
  app.register_blueprint(admin_bp)