from . import db
from .listjadwal import ListJadwal
from .dokter import Dokter
from .poliklinik import Poliklinik
from datetime import datetime
from .reservasi import Reservasi
import locale, uuid

class JadwalPemeriksaan(db.Model):
  __tablename__ = 'jadwalpemeriksaan'
  jadwal_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  listjadwal_id = db.Column(db.String(255), db.ForeignKey('listjadwal.listjadwal_id'), nullable=True)
  dokter_id = db.Column(db.Integer, db.ForeignKey('dokter.dokter_id'), nullable=False)
  poliklinik_id = db.Column(db.Integer, db.ForeignKey('poliklinik.poliklinik_id'), nullable=False)
  
  hari = db.Column(db.String(20), nullable=False)
  jam_mulai = db.Column(db.Time, nullable=False)
  jam_selesai = db.Column(db.Time, nullable=False)
  tanggal = db.Column(db.Date, nullable=False)
  kuota = db.Column(db.Integer, nullable=False)

  listjadwal = db.relationship('ListJadwal', backref='jadwal_pemeriksaan')
  dokter = db.relationship('Dokter', backref='jadwal_pemeriksaan')
  poliklinik = db.relationship('Poliklinik', backref='jadwal_pemeriksaan')
  reservasi = db.relationship('Reservasi', backref='jadwalpemeriksaan')

  @classmethod
  def create(cls, tanggal, list_jadwal_obj, kuota):
    try:
      jadwal = cls(
          tanggal=tanggal,
          listjadwal_id=list_jadwal_obj.listjadwal_id, 
          
          # 2. Snapshot Data (Copy value agar mandiri)
          dokter_id=list_jadwal_obj.dokter_id,
          poliklinik_id=list_jadwal_obj.poliklinik_id,
          hari=list_jadwal_obj.hari,
          jam_mulai=list_jadwal_obj.jam_mulai,
          jam_selesai=list_jadwal_obj.jam_selesai,
          
          kuota=kuota
      )
      db.session.add(jadwal)
      db.session.commit()
      return jadwal, None
    except Exception as e:
      db.session.rollback()
      return None, str(e)

  # def get_sisa_kuota(self, tanggal_target):
  #       if not tanggal_target:
  #           return 0
            
  #       target_date = tanggal_target
  #       if isinstance(tanggal_target, str):
  #           try:
  #               target_date = datetime.strptime(tanggal_target, '%Y-%m-%d').date()
  #           except ValueError:
  #               return 0 
        
  #       terisi = db.session.query(Reservasi).filter_by(
  #           jadwal_id=self.jadwal_id,
  #           tanggal_reservasi=target_date,
  #       ).count()

  #       sisa = self.kuota - terisi
  #       return sisa if sisa > 0 else 0
  
  def get_sisa_kuota(self, tanggal_target=None):
      # Jika tanggal_target tidak dikirim, pakai tanggal dari object self
      target_date = tanggal_target if tanggal_target else self.tanggal
      
      # Pastikan format date benar
      if isinstance(target_date, str):
          try:
              target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
          except ValueError:
              return 0
              
      # Hitung reservasi yang masuk
      terisi = len(self.reservasi) # Menggunakan relationship backref
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

