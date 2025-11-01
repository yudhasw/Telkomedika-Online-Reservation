from . import db

class User(db.Model):
  __abstract__ = 'user'
  nama = db.Column(db.String(255), nullable=False)
  email = db.Column(db.String(255), nullable=False, unique=True)
  password = db.Column(db.String(255), nullable=False)

  def __repr__(self):
    return f"<User {self.nama} ({self.role})>"
  
  def login():
    # Login logic disini 
    return True
  
  def logout():
    # Logout logic disini 
    return True
  
  
