from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .admin import Admin
from .pasien import Pasien
from .dokter import Dokter
from .jadwalPemeriksaan import JadwalPemeriksaan
from .poliklinik import Poliklinik
from .reservasi import Reservasi
from .user import User
