from . import db
from .reservasi import Reservasi
from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

class Pasien(db.Model, UserMixin):
  __tablename__ = "pasien"

  pasien_id = db.Column("pasien_id", db.Integer, primary_key=True, autoincrement=True)
  nama = db.Column("nama_pasien", db.String(255), nullable=False)
  email = db.Column("email_pasien", db.String(255), unique=True, nullable=False)
  nomor_hp = db.Column("nomor_hp", db.String(15))
  jenis_kelamin = db.Column("jenis_kelamin", db.String(9))
  tanggal_lahir = db.Column("tanggal_lahir", db.Date)
  password_hash = db.Column("password_hash", db.String(255), nullable=False)

  reservasi = db.relationship('Reservasi', backref='pasien')

  @property
  def id(self):
      return self.pasien_id

  def __repr__(self):
      return f"<Pasien {self.nama}>"

  @classmethod
  def create(cls, nama, email, password, nomor_hp, jenis_kelamin, tanggal_lahir):
    try:
      password_hash = generate_password_hash(password)
      pasien = Pasien(
          nama=nama,
          email=email,
          password_hash=password_hash,
          nomor_hp=nomor_hp,
          jenis_kelamin=jenis_kelamin,
          tanggal_lahir=tanggal_lahir
      )
      db.session.add(pasien)
      db.session.commit()
      return pasien, None
    except SQLAlchemyError as e:
      db.session.rollback()
      return None, str(e)

  def update_data(self, data):
    try:
      self.nama = data.get('nama', self.nama)
      self.email = data.get('email', self.email)
      self.nomor_hp = data.get('nomor_hp', self.nomor_hp)
      self.jenis_kelamin = data.get('jenis_kelamin', self.jenis_kelamin)
      tgl_lahir = data.get('tanggal_lahir')
      if tgl_lahir:
        self.tanggal_lahir = tgl_lahir
  
      db.session.commit()
      return True, None
    except SQLAlchemyError as e:
      db.session.rollback()
      return False, str(e)
  
  def set_email(self, email):
    try:
      self.email = email
      db.session.commit()
      return True, None
    except Exception as e:
      db.session.rollback()
      return False, str(e)
    
  def set_password(self, password_hash):
    try:
      self.password_hash = generate_password_hash(password_hash)
      db.session.commit()
      return True, None
    except Exception as e:
      db.session.rollback()
      return False, str(e)
      
  def verify_password(self, password):
    try:
      if check_password_hash(self.password_hash, password):
        return True
    except:
      return False
  
  @classmethod
  def authenticate(cls, email, password):
      user = cls.query.filter_by(email=email).first()
      if user and check_password_hash(user.password_hash, password):
          return user
      return None
