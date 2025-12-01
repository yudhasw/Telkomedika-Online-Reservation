from . import db
from .listjadwal import ListJadwal
from .dokter import Dokter
from .poliklinik import Poliklinik
from datetime import datetime
from .reservasi import Reservasi

class JadwalPemeriksaan(db.Model):
  __tablename__ = 'jadwalpemeriksaan'
  jadwal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  listjadwal_id = db.Column(db.String(255), db.ForeignKey('listjadwal.listjadwal_id'), nullable=False)
  tanggal = db.Column(db.Date, nullable=False)
  kuota = db.Column(db.Integer, nullable=False)

  listjadwal = db.relationship('ListJadwal', backref='jadwal_pemeriksaan')
  reservasi = db.relationship('Reservasi', backref='jadwalpemeriksaan')

  def create(tanggal, list_jadwal, kuota):
    jadwal = JadwalPemeriksaan(tanggal=tanggal, listjadwal_id=list_jadwal, kuota=kuota)
    db.session.add(jadwal)
    db.session.commit()

  @property
  def terisi(self):
      return db.session.query(Reservasi).filter_by(jadwal_id=self.jadwal_id).count()

  @property
  def sisa_kuota(self):
      sisa = self.kuota - self.terisi
      return sisa if sisa > 0 else 0

  @classmethod
  def get_filtered_data(cls, poli_id=None, tanggal_str=None):

      query = db.session.query(cls).join(
          ListJadwal, cls.listjadwal_id == ListJadwal.listjadwal_id
      ).join(
          Dokter, ListJadwal.dokter_id == Dokter.dokter_id
      ).join(
          Poliklinik, ListJadwal.poliklinik_id == Poliklinik.poliklinik_id
      )
      # 2. FILTER POLI
      if poli_id:
          query = query.filter(ListJadwal.poliklinik_id == poli_id)
      # 3. FILTER TANGGAL
      if tanggal_str:
          try:
              tanggal_obj = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
              query = query.filter(cls.tanggal == tanggal_obj)
          except ValueError:
              pass

      return query.order_by(
          cls.tanggal.asc(), 
          ListJadwal.jam_mulai.asc()
      ).all()

  def findAll():
    # logic disini
    return True

  def findOne():
    # logic disini 
    return True
  
  def update():
    # logic disini 
    return True
  
  def remove():
    # logic disini 
    return True

