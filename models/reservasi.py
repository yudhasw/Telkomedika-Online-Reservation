# models/reservasi.py
from . import db
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime, timedelta, date

class Reservasi(db.Model):
    reservasi_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.pasien_id'), nullable=False)
    jadwal_id = db.Column(db.String(36), db.ForeignKey('jadwalpemeriksaan.jadwal_id'), nullable=False)
    no_urut = db.Column(db.Integer, nullable=False)
    tanggal_reservasi = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Menunggu')
    is_reminded = db.Column(db.Boolean, default=False)

    @classmethod
    def create(cls, pasien_id, jadwal_id, no_urut, tanggal, status, is_reminded):
        try:
            reservasi = cls(
                pasien_id=pasien_id,
                jadwal_id=jadwal_id,
                no_urut=no_urut,
                tanggal_reservasi=tanggal,
                status=status,
                is_reminded=is_reminded
            )
            db.session.add(reservasi)
            db.session.commit()
            return reservasi, None
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, str(e)

    def update_status(self, new_status: str) -> tuple[bool, str | None]:
        try:
            self.status = new_status
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def delete(self) -> tuple[bool, str | None]:
        try:
            db.session.delete(self)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @property
    def estimasi_waktu(self):
        try:
            jam_mulai = self.jadwalpemeriksaan.jam_mulai

            dummy_date = date.today()
            start_dt = datetime.combine(dummy_date, jam_mulai)

            tambahan_menit = (self.no_urut - 1) * 20

            estimasi_dt = start_dt + timedelta(minutes=tambahan_menit)

            return estimasi_dt.strftime("%H:%M")

        except Exception:
            return "Sesuai Antrian"

    @classmethod
    def get_reservation_data(cls, pasien_id: int):
        data = (
            cls.query
            .filter_by(pasien_id=pasien_id)
            .order_by(cls.tanggal_reservasi.desc())
            .all()
        )
        return data or []

    @classmethod
    def get_upcoming_and_history(cls, pasien_id: int):
        data = cls.get_reservation_data(pasien_id)
        today = date.today()
        upcoming, history = [], []

        for res in data:
            if res.status in ['Menunggu', 'Dikonfirmasi'] and res.tanggal_reservasi >= today:
                upcoming.append(res)
            else:
                history.append(res)

        return upcoming, history

    @classmethod
    def cancel_reservasi(cls, reservasi_id: str, pasien_id: int):
        reservasi = cls.query.get(reservasi_id)

        if not reservasi:
            # data tidak ditemukan
            return False, "Data reservasi tidak ditemukan."

        if reservasi.pasien_id != pasien_id:
            # bukan pemilik reservasi
            return False, "Anda tidak memiliki akses untuk membatalkan reservasi ini."

        if reservasi.status in ['Selesai', 'Dibatalkan', 'Dalam Proses']:
            # sudah tidak bisa dibatalkan
            return False, "Reservasi ini sudah tidak bisa dibatalkan."

        try:
            reservasi.status = 'Dibatalkan'
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def set_status(self, status):
        try:
            self.status = status
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
