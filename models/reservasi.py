from . import db
from sqlalchemy.exc import SQLAlchemyError
import uuid

class Reservasi(db.Model):
  reservasi_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.pasien_id'), nullable=False)
  jadwal_id = db.Column(db.Integer, db.ForeignKey('jadwalpemeriksaan.jadwal_id'), nullable=False)
  no_urut = db.Column(db.Integer, nullable=False)
  tanggal_reservasi = db.Column(db.Date, nullable=False)
  status = db.Column(db.String(50), default='Menunggu')
  
  @classmethod
  def create(pasien_id, jadwal_id, no_urut, tanggal, status):
    try:
      reservasi = Reservasi(
        pasien_id=pasien_id, 
        jadwal_id=jadwal_id, 
        no_urut=no_urut, 
        tanggal_reservasi=tanggal, 
        status='Menuggu'
      )
      db.session.add(reservasi)
      db.session.commit()
      return reservasi, None  
    except SQLAlchemyError as e:
      db.session.rollback
      return None, str(e)


  def findAll():
    # logic disini
    return True

  def findOne():
    # logic disini 
    return True
  
  def update():
    # Logout logic disini 
    return True
  
  def remove():
    # Logout logic disini 
    return True