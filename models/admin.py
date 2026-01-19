from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class Admin(db.Model, UserMixin):
  __tablename__ = 'admin'
  admin_id = db.Column("admin_id", db.Integer, primary_key=True, autoincrement=True)
  nama = db.Column("nama_admin", db.String(255), nullable=False)
  email = db.Column("email_admin", db.String(255), unique=True, nullable=False)
  password_hash = db.Column("password_hash", db.String(255), nullable=False)

  @property
  def id(self):
      return self.admin_id

  def __repr__(self):
      return f"<Admin {self.nama}>"
  
  def create_admin(nama, email, password):
    hashed_pass = generate_password_hash(password)
    admin = Admin(nama=nama, email=email, password_hash=hashed_pass)
    db.session.add(admin)
    db.session.commit()

  def find_admin(id):
    admin = User.query.get(id)
    if admin:
      return True
    return False 
