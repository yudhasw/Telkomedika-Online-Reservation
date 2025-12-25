from . import db
from .listjadwal import ListJadwal
from .dokter import Dokter
from .poliklinik import Poliklinik
from datetime import datetime, date, timedelta
from .reservasi import Reservasi
import uuid

class JadwalPemeriksaan(db.Model):
  __tablename__ = 'jadwalpemeriksaan'
  jadwal_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  listjadwal_id = db.Column(db.Integer, db.ForeignKey('listjadwal.listjadwal_id'))
  tanggal = db.Column(db.Date, nullable=False)
  kuota = db.Column(db.Integer, nullable=False)
  hari = db.Column(db.String(20), nullable=False)
  dokter_id = db.Column(db.Integer, db.ForeignKey('dokter.dokter_id'), nullable=False)
  poliklinik_id = db.Column(db.Integer, db.ForeignKey('poliklinik.poliklinik_id'), nullable=False)
  jam_mulai = db.Column("jam_mulai", db.Time, nullable=False)
  jam_selesai = db.Column("jam_selesai", db.Time, nullable=False)

  listjadwal = db.relationship('ListJadwal', backref='jadwal_pemeriksaan')
  reservasi = db.relationship('Reservasi', backref='jadwalpemeriksaan')
  dokter = db.relationship('Dokter', backref='jadwal_pemeriksaan')
  poliklinik = db.relationship('Poliklinik', backref='jadwal_pemeriksaan')

  @classmethod
  def create(cls, tanggal, list_jadwal, kuota, hari, dokter_id, poliklinik_id, jam_mulai, jam_selesai):
    try:
        jadwal = cls(
            tanggal=tanggal, 
            listjadwal_id=list_jadwal, 
            kuota=kuota,
            hari=hari,
            dokter_id=dokter_id,
            poliklinik_id=poliklinik_id,
            jam_mulai=jam_mulai,
            jam_selesai=jam_selesai
        )
        db.session.add(jadwal)
        db.session.commit()
        return jadwal, None 
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

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

        today = datetime.now().date()

        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        query = db.session.query(cls).join(
            Dokter, cls.dokter_id == Dokter.dokter_id
        ).join(
            Poliklinik, cls.poliklinik_id == Poliklinik.poliklinik_id
        ).filter(     
            cls.hari == nama_hari, cls.tanggal >= week_start, cls.tanggal <= week_end
            # cls.tanggal == tanggal_obj
        )
    
        if poli_id:
          query = query.filter(cls.poliklinik_id == poli_id)

        return query.order_by(cls.jam_mulai.asc()).all()
  
  @classmethod
  def get_all_data(cls):
      
      today = datetime.now().date()

      week_start = today - timedelta(days=today.weekday())
      week_end = week_start + timedelta(days=6)

      return db.session.query(cls).join(Dokter).join(Poliklinik).filter(cls.tanggal >= week_start,cls.tanggal <= week_end).order_by(cls.hari, cls.jam_mulai).all()
