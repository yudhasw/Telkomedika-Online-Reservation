from . import db

class Poliklinik(db.Model):
  __tablename__ = 'poliklinik'
  poliklinik_id = db.Column("poliklinik_id", db.Integer, primary_key=True, autoincrement=True)
  nama_poli = db.Column("nama_poli", db.String(255), nullable=False)
  deskripsi = db.Column("deskripsi", db.String(255))

  list_jadwal = db.relationship("ListJadwal", back_populates="poliklinik")
  dokter_list = db.relationship("Dokter", back_populates="poliklinik")
  
  @classmethod
  def create(cls, nama_poli, deskripsi):
    poliklinik = cls(nama_poli=nama_poli, deskripsi=deskripsi)
    db.session.add(poliklinik)
    db.session.commit()
    return poliklinik
  
  @classmethod
  def get_all_data(cls):
    poli = cls.query.all()

    if poli: 
      return poli

    return None