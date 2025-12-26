from . import db
from .reservasi import Reservasi
from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError

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
  def create(cls, nama, email, password_hash, nomor_hp, jenis_kelamin, tanggal_lahir):
    try:
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
      self.password_hash = password_hash
      db.session.commit()
      return True, None
    except Exception as e:
      db.session.rollback()
      return False, str(e)

  def get_upcoming_reservasi(self, tdate):
    try:
      upcoming = Reservasi.query.filter(
            Reservasi.pasien_id == self.pasien_id,
            Reservasi.status.in_(['Menunggu', 'Dikonfirmasi']),
            Reservasi.tanggal_reservasi >= tdate
        ).all()
      
      return upcoming
    except Exception as e:
      print(f"Error retrieving Upcoming: {e}")
      return None
    
  def get_history_reservasi(self, tdate):
    try:
      history = Reservasi.query.filter(
              Reservasi.pasien_id == self.pasien_id,
              (Reservasi.status.notin_(['Menunggu', 'Dikonfirmasi'])) | (Reservasi.tanggal_reservasi < tdate)
          ).order_by(Reservasi.tanggal_reservasi.desc()).all()
      return history
    except Exception as e:
      print(f"Error history Upcoming: {e}")
      return None