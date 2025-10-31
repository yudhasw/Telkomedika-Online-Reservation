from . import db
from models.dokter import Dokter

class Dokter(Dokter):
  __tablename__ = 'dokter'
  dokter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nama_dokter = db.Column(db.String(255), nullable=True)
  spesialisasi = db.Column(db.String(60))

  

  def create(nama, spesialis):
    dokter = Dokter(nama=nama, spesialis=spesialis)
    db.session.add(dokter)
    db.session.commit()

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