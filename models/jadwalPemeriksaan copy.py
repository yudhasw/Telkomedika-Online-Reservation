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

  @property
  def terisi(self):
      return db.session.query(Reservasi).filter_by(jadwal_id=self.jadwal_id).count()

  @property
  def sisa_kuota(self):
      sisa = self.kuota - self.terisi
      return sisa if sisa > 0 else 0

  @classmethod
  def get_filtered_data(cls, poli_id=None, tanggal_str=None):
        if not tanggal_str:
            return []

        try:
            tanggal_obj = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        except ValueError:
            return []

        days_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
        nama_hari = days_map[tanggal_obj.weekday()]

        query_template = ListJadwal.query.filter_by(hari=nama_hari)
        
        if poli_id:
            query_template = query_template.filter_by(poliklinik_id=poli_id)
            
        templates = query_template.all()

        jadwal_baru_dibuat = False
        
        for template in templates:
            existing_jadwal = cls.query.filter_by(
                listjadwal_id=template.listjadwal_id,
                tanggal=tanggal_obj
            ).first()

            if not existing_jadwal:
                new_jadwal = cls(
                    listjadwal_id=template.listjadwal_id,
                    tanggal=tanggal_obj,
                    kuota=10 
                )
                db.session.add(new_jadwal)
                jadwal_baru_dibuat = True
        
        if jadwal_baru_dibuat:
            db.session.commit()

        query = db.session.query(cls).join(
            ListJadwal, cls.listjadwal_id == ListJadwal.listjadwal_id
        ).join(
            Dokter, ListJadwal.dokter_id == Dokter.dokter_id
        ).join(
            Poliklinik, ListJadwal.poliklinik_id == Poliklinik.poliklinik_id
        ).filter(
            cls.tanggal == tanggal_obj
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

