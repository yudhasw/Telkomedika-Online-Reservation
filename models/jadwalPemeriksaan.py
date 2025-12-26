from . import db
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

    @classmethod
    def delete_one(cls, jadwal_id: str) -> tuple[bool, str | None]:
        jadwal = cls.query.get(jadwal_id)
        if not jadwal:
            return False, "Data tidak ditemukan"

        jumlah_reservasi = len(jadwal.reservasi)
        if jumlah_reservasi > 0:
            return False, f"Terdapat {jumlah_reservasi} pasien yang sudah reservasi di jadwal ini."

        try:
            db.session.delete(jadwal)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @classmethod
    def delete_week(cls, scope: str) -> tuple[int, str | None]:
        try:
            today = date.today()

            if scope == 'current':
                start_date = today - timedelta(days=today.weekday())
            else:
                days_to_monday = 0 - today.weekday()
                if days_to_monday <= 0:
                    days_to_monday += 7
                start_date = today + timedelta(days=days_to_monday)

            end_date = start_date + timedelta(days=6)

            deleted_count = cls.query.filter(
                cls.tanggal >= start_date,
                cls.tanggal <= end_date
            ).delete()

            db.session.commit()
            return deleted_count, None
        except Exception as e:
            db.session.rollback()
            return 0, str(e)

    def update(self, jam_mulai_str: str | None, jam_selesai_str: str | None, kuota: int | None) -> tuple[bool, str | None]:
        try:
            if jam_mulai_str:
                self.jam_mulai = datetime.strptime(jam_mulai_str, '%H:%M').time()
            if jam_selesai_str:
                self.jam_selesai = datetime.strptime(jam_selesai_str, '%H:%M').time()

            if self.jam_selesai <= self.jam_mulai:
                return False, "Jam Selesai tidak boleh lebih awal dari Jam Mulai"

            if kuota:
                self.kuota = int(kuota)
            else:
                dummy_date = date.today()
                start_dt = datetime.combine(dummy_date, self.jam_mulai)
                end_dt = datetime.combine(dummy_date, self.jam_selesai)
                durasi = (end_dt - start_dt).total_seconds() / 60
                self.kuota = int(durasi / 10)

            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)