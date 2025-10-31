from . import db
from models.user import User
from werkzeug.security import generate_password_hash

class Pasien(User):
  __tablename__ = 'pasien'
  pasien_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nomor_hp = db.Column(db.String(15))
  jenis_kelamin = db.Column(db.String(9))
  tanggal_lahir = db.Column(db.Date)

  reservasi = db.relationship('Reservasi', backref='pasien')

  def create(nama, email, password, nomor_hp, jenis_kelamin, tanggal_lahir):
    # logic disini
    hashed_pass = generate_password_hash(password)
    pasien = Pasien(
        nama=nama,
        email=email,
        password=hashed_pass,
        nomor_hp=nomor_hp,
        jenis_kelamin=jenis_kelamin,
        tanggal_lahir=tanggal_lahir
    )
    db.session.add(pasien)
    db.session.commit()
  
  def findAll():
    # logic disini
    return True

  def findOne():
    # logic disini 
    return True

  def update():
    # logic disini 
    return True
  
  def remove():
    # logic disini
    return True

  def login():
    # logic disini
    return True
  
  def logout():
    # logic disini 
    return True

 