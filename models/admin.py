from . import db
from models.user import User
from werkzeug.security import generate_password_hash

class Admin(User):
  __tablename__ = 'admin'
  admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  def create_admin(nama, email, password):
    hashed_pass = generate_password_hash(password)
    admin = Admin(nama=nama, email=email, password=hashed_pass)
    db.session.add(admin)
    db.session.commit()

  def find_admin(id):
    admin = User.query.get(id)
    if admin:
      return True
    return False 
  
  def update():
    # Logout logic disini 
    return True
  
  def remove():
    # Logout logic disini 
    return True