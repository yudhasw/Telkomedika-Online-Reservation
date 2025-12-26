from . import db
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

  @property
  def id(self):
      return self.pasien_id

  def __repr__(self):
      return f"<Pasien {self.nama}>"

  reservasi = db.relationship('Reservasi', backref='pasien')

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

  @classmethod
  def update(nama, email, password, nomor_hp, jenis_kelamin, tanggal_lahir):
    try:
      pasien = Pasien(
          nama=nama,
          email=email,
          password=password,
          nomor_hp=nomor_hp,
          jenis_kelamin=jenis_kelamin,
          tanggal_lahir=tanggal_lahir
      )
      db.session.commit()
      return pasien, None
    except SQLAlchemyError as e:
      db.session.rollback
      return None, str(e)
    
  def set_password(self, password_hash):
    try:
      self.password_hash = password_hash
      db.session.commit()
      return True
    except Exception as e:
      db.session.rollback()
      return False

  def apply_profile_update(self, cleaned_data: dict) -> str:
    self.nama = cleaned_data["nama"]
    self.nomor_hp = cleaned_data["phone"]
    self.jenis_kelamin = cleaned_data["jenis_kelamin"]
    self.tanggal_lahir = cleaned_data["tgl_lahir"]
    return cleaned_data["email"]

  def verify_password(self, raw_password: str) -> bool:
    return check_password_hash(self.password_hash, raw_password)

  def set_password_plain(self, new_password: str):
    try:
        self.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)
  
  @classmethod
  def authenticate(cls, email, password):
      user = cls.query.filter_by(email=email).first()
      if user and check_password_hash(user.password_hash, password):
          return user
      return None


 