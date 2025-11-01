from . import db
from flask_login import UserMixin
from models.user import User
from werkzeug.security import generate_password_hash

class Pasien(db.Model, UserMixin):
  __tablename__ = "pasien"

  pasien_id     = db.Column("pasien_id", db.Integer, primary_key=True, autoincrement=True)
  nama          = db.Column("nama_pasien", db.String(255), nullable=False)                  # <- map ke nama_pasien
  email         = db.Column("email_pasien", db.String(255), unique=True, nullable=False)    # <- map ke email_pasien
  nomor_hp      = db.Column("nomor_hp", db.String(15))
  jenis_kelamin = db.Column("jenis_kelamin", db.String(9))
  tanggal_lahir = db.Column("tanggal_lahir", db.Date)
  password      = db.Column("password", db.String(255), nullable=False)

    # HANYA kalau tabelmu benar2 punya kolom 'role'
    # role          = db.Column("role", db.String(20))

    # Relasi: pastikan FK di Reservasi = 'pasien.pasien_id'
    # reservasi = db.relationship("Reservasi", backref="pasien", lazy=True)
  @property
  def id(self):
      return self.pasien_id

  def __repr__(self):
      return f"<Pasien {self.nama}>"

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

 