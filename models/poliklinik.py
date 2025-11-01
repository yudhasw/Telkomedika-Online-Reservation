from . import db

class Poliklinik(db.Model):
  __tablename__ = 'poliklinik'
  poliklinik_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  dokter_id = db.Column(db.Integer, db.ForeignKey('dokter.dokter_id'), nullable=False)
  nama_unit = db.Column(db.String(255), nullable=False)
  deskripsi = db.Column(db.String(255))

  dokter = db.relationship('Dokter', backref='poliklinik')
  
  def create(nama_unit, deskripsi):
    poliklinik = Poliklinik(nama_unit=nama_unit, deskripsi=deskripsi)
    db.session.add(poliklinik)
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