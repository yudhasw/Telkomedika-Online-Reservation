from . import db

class JadwalPemeriksaan(db.Model):
  __tablename__ = 'jadwalpemeriksaan'
  jadwal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  listjadwal_id = db.Column(db.String(255), db.ForeignKey('listjadwal.listjadwal_id'), nullable=False)
  poliklinik_id = db.Column(db.Integer, db.ForeignKey('poliklinik.poliklinik_id'), nullable=False)
  tanggal = db.Column(db.Date, nullable=False)
  kuota = db.Column(db.Integer, nullable=False)

  poliklinik = db.relationship('Poliklinik', backref='jadwalpemeriksaan')
  reservasi = db.relationship('Reservasi', backref='jadwalpemeriksaan')

  def create(tanggal, list_jadwal, kuota):
    jadwal = JadwalPemeriksaan(tanggal=tanggal, listjadwal_id=list_jadwal, kuota=kuota)
    db.session.add(jadwal)
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

