from . import db
from .dokter import Dokter
from .poliklinik import Poliklinik

class ListJadwal(db.Model):
  __tablename__ = 'listjadwal'

  listjadwal_id = db.Column("listjadwal_id", db.Integer, primary_key=True, autoincrement=True)
  jam_mulai = db.Column("jam_mulai", db.Time, nullable=False)
  jam_selesai = db.Column("jam_selesai", db.Time, nullable=False)
  dokter_id = db.Column(db.Integer, db.ForeignKey("dokter.dokter_id"), nullable=False)
  poliklinik_id = db.Column(db.Integer, db.ForeignKey("poliklinik.poliklinik_id"), nullable=False)
  hari = db.Column(db.String(20), nullable=False)

  dokter = db.relationship("Dokter", back_populates="list_jadwal")
  poliklinik = db.relationship("Poliklinik", back_populates="list_jadwal")

  def get_data():
    data = (
      ListJadwal.query
      .join(Dokter, ListJadwal.dokter_id == Dokter.dokter_id)
      .join(Poliklinik, ListJadwal.poliklinik_id == Poliklinik.poliklinik_id)
      .all()
    )
    if data:
      return data
    
    return None
