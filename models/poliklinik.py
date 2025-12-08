from . import db

class Poliklinik(db.Model):
  __tablename__ = 'poliklinik'
  poliklinik_id = db.Column("poliklinik_id", db.Integer, primary_key=True, autoincrement=True)
  nama_poli = db.Column("nama_poli", db.String(255), nullable=False)
  deskripsi = db.Column("deskripsi", db.String(255))

  # Relasi ke ListJadwal (Sudah Benar)
  list_jadwal = db.relationship("ListJadwal", back_populates="poliklinik")
  dokter_list = db.relationship("Dokter", back_populates="poliklinik")
  
  @classmethod
  def create(cls, nama_poli, deskripsi):
    # PERBAIKAN: Gunakan cls() dan sesuaikan nama argumen
    poliklinik = cls(nama_poli=nama_poli, deskripsi=deskripsi)
    db.session.add(poliklinik)
    db.session.commit()
    return poliklinik

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