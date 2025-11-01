from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Admin(db.Model, UserMixin):
  __tablename__ = 'admin'
  admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nama = db.Column(db.String(255), nullable=False)
  email = db.Column(db.String(255), nullable=False, unique=True)
  password = db.Column(db.String(255), nullable=False)

  def __repr__(self):
    return f"<Admin {self.nama}>"

class Pasien(db.Model, UserMixin):
    __tablename__ = "pasien"

    pasien_id     = db.Column("pasien_id", db.Integer, primary_key=True, autoincrement=True)
    nama          = db.Column("nama_pasien", db.String(255), nullable=False)                  # <- map ke nama_pasien
    email         = db.Column("email_pasien", db.String(255), unique=True, nullable=False)    # <- map ke email_pasien
    nomor_hp      = db.Column("nomor_hp", db.String(15))
    jenis_kelamin = db.Column("jenis_kelamin", db.String(9))
    tanggal_lahir = db.Column("tanggal_lahir", db.Date)
    password      = db.Column("password", db.String(255), nullable=False)

    # HANYA kalau tabelmu benar2 punya kolom 'role'
    # role          = db.Column("role", db.String(20))

    # Relasi: pastikan FK di Reservasi = 'pasien.pasien_id'
    # reservasi = db.relationship("Reservasi", backref="pasien", lazy=True)

    # Alias untuk Flask-Login (jangan buat Column 'id')
    @property
    def id(self):
        return self.pasien_id

    def __repr__(self):
        return f"<Pasien {self.nama}>"
  
class Poliklinik(db.Model):
  __tablename__ = 'poliklinik'
  poliklinik_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nama_unit = db.Column(db.String(255), nullable=False)
  deskripsi = db.Column(db.String(255))

  list_jadwal = db.relationship('ListJadwal', backref='poliklinik', lazy=True)

  def __repr__(self):
    return f"<Poliklinik {self.nama_unit}>"
  
class Dokter(db.Model):
  __tablename__ = 'dokter'
  dokter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  nama = db.Column(db.String(255), nullable=True)
  spesialisasi = db.Column(db.String(60))

  list_jadwal = db.relationship('ListJadwal', backref='dokter', lazy=True)

  def __repr__(self):
    return f"<Dokter {self.nama}>"

class ListJadwal(db.Model):
    __tablename__ = 'listjadwal'
    listjadwal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dokter_id = db.Column(db.Integer, db.ForeignKey('dokter.dokter_id'), nullable=False)
    poliklinik_id = db.Column(db.Integer, db.ForeignKey('poliklinik.poliklinik_id'), nullable=False)
    jam_mulai = db.Column(db.Time, nullable=False)
    jam_selesai = db.Column(db.Time, nullable=False)

    jadwal_pemeriksaan = db.relationship('JadwalPemeriksaan', backref='listjadwal', lazy=True)

    def __repr__(self):
        return f"<ListJadwal Dokter={self.dokter_id}, Poli={self.poliklinik_id}>"

class JadwalPemeriksaan(db.Model):
    __tablename__ = 'jadwalpemeriksaan'
    jadwal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listjadwal_id = db.Column(db.Integer, db.ForeignKey('listjadwal.listjadwal_id'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    kuota = db.Column(db.Integer, nullable=False)

    reservasi = db.relationship('Reservasi', backref='jadwal', lazy=True)

    def __repr__(self):
        return f"<JadwalPemeriksaan ID={self.jadwal_id} Tanggal={self.tanggal}>"

class Reservasi(db.Model):
    __tablename__ = 'reservasi'
    reservasi_id = db.Column(db.String(50), primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('pasien.pasien_id'), nullable=False)
    jadwal_id = db.Column(db.Integer, db.ForeignKey('jadwalpemeriksaan.jadwal_id'), nullable=False)
    no_urut = db.Column(db.Integer, nullable=False)
    tanggal_reservasi = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Menunggu')

    def __repr__(self):
        return f"<Reservasi {self.reservasi_id} Pasien={self.pasien_id}>"
  
