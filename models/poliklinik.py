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
  
  def delete(self) -> tuple[bool, str | None, int | None]:
    if len(self.dokter_list) > 0:
        return (
            False,
            f'Masih ada {len(self.dokter_list)} dokter yang terdaftar di poli ini. Pindahkan atau hapus dokter tersebut terlebih dahulu.',
            409,
        )
    if len(self.list_jadwal) > 0:
        return (
            False,
            'Masih ada template jadwal yang menggunakan poli ini.',
            409,
        )
    try:
        db.session.delete(self)
        db.session.commit()
        return True, None, None
    except Exception as e:
        db.session.rollback()
        return False, str(e), 500