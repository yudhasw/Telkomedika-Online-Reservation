from . import db
from .poliklinik import Poliklinik

class Dokter(db.Model):
    __tablename__ = 'dokter'
    
    dokter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_dokter = db.Column(db.String(255), nullable=True)
    spesialisasi = db.Column(db.String(60))
    poliklinik_id = db.Column(db.Integer, db.ForeignKey('poliklinik.poliklinik_id', ondelete='SET NULL'), nullable=True)
    
    poliklinik = db.relationship("Poliklinik", back_populates="dokter_list")
    list_jadwal = db.relationship("ListJadwal", back_populates="dokter")
    
    def to_dict(self):
        return {
            "id": self.dokter_id,
            "name": self.nama_dokter,
            "poli": self.spesialisasi
        }
    
    @staticmethod
    def create(nama, spesialis, poli_id=None):
        try:
            dokter = Dokter(nama_dokter=nama, spesialisasi=spesialis, poliklinik_id=poli_id)
            db.session.add(dokter)
            db.session.commit()
            return True, "Berhasil menambahkan dokter"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @classmethod
    def update(cls, id: int, nama: str, poli_id: int) -> tuple[bool, str | None]:
        try:
            dokter = cls.query.get(id)
            if not dokter:
                return False, "Dokter tidak ditemukan"

            poli = Poliklinik.query.get(poli_id)
            nama_spesialisasi = poli.nama_poli if poli else "Umum"

            dokter.nama_dokter = nama
            dokter.spesialisasi = nama_spesialisasi
            dokter.poliklinik_id = poli_id

            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def delete(self) -> tuple[bool, str | None]:
        if len(self.list_jadwal) > 0:
            return False, "Dokter ini masih memiliki jadwal praktek. Hapus jadwalnya terlebih dahulu."
        try:
            db.session.delete(self)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @staticmethod
    def findAll():
        return Dokter.query.all()

    @staticmethod
    def findOne(id):
        return Dokter.query.get(id)