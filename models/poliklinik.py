from . import db

class Poliklinik(db.Model):
  __tablename__ = 'poliklinik'
  poliklinik_id = db.Column("poliklinik_id",db.Integer, primary_key=True, autoincrement=True)
  nama_poli = db.Column("nama_poli", db.String(255), nullable=False)
  deskripsi = db.Column("deskripsi",db.String(255))

  list_jadwal = db.relationship("ListJadwal", back_populates="poliklinik")
  
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