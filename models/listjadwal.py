from . import db
from .dokter import Dokter
from .poliklinik import Poliklinik
from .jadwalPemeriksaan import JadwalPemeriksaan
from datetime import datetime

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
  
  @classmethod
  def update_all(cls, doctor_id: int, schedules: list[dict]) -> tuple[bool, str | None]:
    try:
        dokter = Dokter.query.get(doctor_id)
        if not dokter:
            return False, "Dokter tidak ditemukan"

        # Tentukan poli dari spesialisasi
        nama_spesialisasi = dokter.spesialisasi
        poli = Poliklinik.query.filter(
            Poliklinik.nama_poli.ilike(f"%{nama_spesialisasi}%")
        ).first()

        if poli:
            target_poli_id = poli.poliklinik_id
        else:
            poli_umum = Poliklinik.query.filter(
                Poliklinik.nama_poli.ilike("%Umum%")
            ).first()
            target_poli_id = poli_umum.poliklinik_id if poli_umum else 1

        # Hapus jadwal lama + putus relasi JadwalPemeriksaan
        jadwal_lama = cls.query.filter_by(dokter_id=doctor_id).all()
        for jadwal in jadwal_lama:
            jp_terkait = JadwalPemeriksaan.query.filter_by(
                listjadwal_id=jadwal.listjadwal_id
            ).all()
            for jp in jp_terkait:
                jp.listjadwal_id = None
            db.session.delete(jadwal)

        # Tambah jadwal baru
        for item in schedules:
            try:
                jam_mulai = datetime.strptime(item["start"], "%H:%M").time()
                jam_selesai = datetime.strptime(item["end"], "%H:%M").time()
            except ValueError:
                continue

            new_jadwal = cls(
                dokter_id=doctor_id,
                poliklinik_id=target_poli_id,
                hari=item["day"],
                jam_mulai=jam_mulai,
                jam_selesai=jam_selesai,
            )
            db.session.add(new_jadwal)

        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, str(e)
