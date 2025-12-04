from . import db
from .listjadwal import ListJadwal
from .dokter import Dokter
from .poliklinik import Poliklinik
from datetime import datetime
from .reservasi import Reservasi
import locale

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

  def get_sisa_kuota(self, tanggal_target):
        if not tanggal_target:
            return 0
            
        target_date = tanggal_target
        if isinstance(tanggal_target, str):
            try:
                target_date = datetime.strptime(tanggal_target, '%Y-%m-%d').date()
            except ValueError:
                return 0 
        
        terisi = db.session.query(Reservasi).filter_by(
            jadwal_id=self.jadwal_id,
            tanggal_reservasi=target_date,
        ).count()

        sisa = self.kuota - terisi
        return sisa if sisa > 0 else 0

  @classmethod
  def get_filtered_data(cls, poli_id, tanggal_str):
        if not tanggal_str:
          return []
      
        try:
            tanggal_obj = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        except ValueError:
            return []

        days_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
        nama_hari = days_map[tanggal_obj.weekday()]

        query = db.session.query(cls).join(
              ListJadwal, cls.listjadwal_id == ListJadwal.listjadwal_id
          ).join(
              Dokter, ListJadwal.dokter_id == Dokter.dokter_id
          ).join(
              Poliklinik, ListJadwal.poliklinik_id == Poliklinik.poliklinik_id
          ).filter(     
              ListJadwal.hari == nama_hari
          )
    
        if poli_id:
          query = query.filter(ListJadwal.poliklinik_id == poli_id)

        return query.order_by(ListJadwal.jam_mulai.asc()).all()

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

