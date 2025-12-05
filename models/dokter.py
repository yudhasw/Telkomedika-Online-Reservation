from . import db

class Dokter(db.Model):
    __tablename__ = 'dokter'
    
    dokter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_dokter = db.Column(db.String(255), nullable=True)
    spesialisasi = db.Column(db.String(60))

    # Relasi jadwal (biarkan seperti semula)
    list_jadwal = db.relationship("ListJadwal", back_populates="dokter")

    # Helper untuk mengubah objek database menjadi dictionary (agar bisa dibaca Javascript)
    def to_dict(self):
        return {
            "id": self.dokter_id,
            "name": self.nama_dokter,
            "poli": self.spesialisasi
        }

    @staticmethod
    def create(nama, spesialis):
        try:
            dokter = Dokter(nama_dokter=nama, spesialisasi=spesialis)
            db.session.add(dokter)
            db.session.commit()
            return True, "Berhasil menambahkan dokter"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def findAll():
        return Dokter.query.all()

    @staticmethod
    def findOne(id):
        return Dokter.query.get(id)
    
    def update(self, nama, spesialis):
        try:
            self.nama_dokter = nama
            self.spesialisasi = spesialis
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
    
    def remove(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False