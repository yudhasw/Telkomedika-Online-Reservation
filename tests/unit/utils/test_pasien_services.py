from datetime import date
import pytest

from utils.pasien_services import (
    nomorUrut,
    get_next_date,
    validate_profile_update,
    validate_manual_reservation,
)
from models import Pasien, db


# -------------------------
# nomorUrut (pakai monkeypatch query)
# -------------------------
class _FakeFilter:
    def __init__(self, count_value: int):
        self._count_value = count_value

    def count(self):
        return self._count_value


class _FakeReservasiQuery:
    def __init__(self, count_value: int):
        self._count_value = count_value

    def filter_by(self, **kwargs):
        return _FakeFilter(self._count_value)


class _FakeJadwal:
    def __init__(self, kuota: int):
        self.kuota = kuota


class _FakeJadwalQuery:
    def __init__(self, jadwal):
        self._jadwal = jadwal

    def get(self, jadwal_id):
        return self._jadwal


def test_nomorurut_returns_none_if_jadwal_not_found(monkeypatch):
    import utils.pasien_services as ps

    monkeypatch.setattr(ps, "JadwalPemeriksaan", type("X", (), {"query": _FakeJadwalQuery(None)}))
    monkeypatch.setattr(ps, "Reservasi", type("Y", (), {"query": _FakeReservasiQuery(0)}))

    assert nomorUrut("jadwal-x", date.today()) is None


def test_nomorurut_returns_next_number_when_under_quota(monkeypatch):
    import utils.pasien_services as ps

    monkeypatch.setattr(ps, "JadwalPemeriksaan", type("X", (), {"query": _FakeJadwalQuery(_FakeJadwal(kuota=5))}))
    monkeypatch.setattr(ps, "Reservasi", type("Y", (), {"query": _FakeReservasiQuery(3)}))  # sudah 3 reservasi

    assert nomorUrut("jadwal-1", date.today()) == 4


def test_nomorurut_returns_none_when_quota_full(monkeypatch):
    import utils.pasien_services as ps

    monkeypatch.setattr(ps, "JadwalPemeriksaan", type("X", (), {"query": _FakeJadwalQuery(_FakeJadwal(kuota=3))}))
    monkeypatch.setattr(ps, "Reservasi", type("Y", (), {"query": _FakeReservasiQuery(3)}))  # full

    assert nomorUrut("jadwal-1", date.today()) is None


# -------------------------
# get_next_date (patch date.today)
# -------------------------
def test_get_next_date_returns_next_week_when_same_day(monkeypatch):
    import utils.pasien_services as ps

    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 1, 6)  # Senin

    monkeypatch.setattr(ps, "date", FakeDate)

    # target Senin -> harus minggu depan (bukan hari ini)
    assert get_next_date("Senin") == "2025-01-13"


def test_get_next_date_returns_correct_future_day(monkeypatch):
    import utils.pasien_services as ps

    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2025, 1, 6)  # Senin

    monkeypatch.setattr(ps, "date", FakeDate)

    assert get_next_date("Rabu") == "2025-01-08"


# -------------------------
# validate_profile_update (pakai DB test)
# -------------------------
def test_validate_profile_update_success_same_user_email(app, db):
    p = Pasien(nama="A", email="a@test.com", nomor_hp="081234567890", password_hash="hash")
    db.session.add(p)
    db.session.commit()

    data = {
        "nama": "A Updated",
        "email": "a@test.com",  # email sama (harus boleh)
        "nomor_hp": "0812-345-678-90",
        "tanggal_lahir": "2000-01-01",
        "jenis_kelamin": "Laki-laki",
    }

    ok, errors, cleaned = validate_profile_update(data, current_user_id=p.pasien_id)
    assert ok is True
    assert all(v is None for v in errors.values())
    # phone harus dibersihin dari spasi/dash
    assert cleaned["phone"] == "081234567890"


def test_validate_profile_update_rejects_email_used_by_other_user(app, db):
    p1 = Pasien(nama="A", email="a@test.com", nomor_hp="081234567890", password_hash="hash")
    p2 = Pasien(nama="B", email="b@test.com", nomor_hp="081234567891", password_hash="hash")
    db.session.add_all([p1, p2])
    db.session.commit()

    data = {
        "nama": "B Updated",
        "email": "a@test.com",  # punya user lain
        "nomor_hp": "081234567891",
        "tanggal_lahir": "2000-01-01",
        "jenis_kelamin": "Laki-laki",
    }

    ok, errors, cleaned = validate_profile_update(data, current_user_id=p2.pasien_id)
    assert ok is False
    assert errors["email"] == "Email sudah digunakan oleh pengguna lain."


# -------------------------
# validate_manual_reservation (pure)
# -------------------------
def test_validate_manual_reservation_rejects_missing_fields():
    ok, errors = validate_manual_reservation({"nama": "", "email": "", "phone": ""})
    assert ok is False
    assert "Nama pasien wajib diisi." in errors
    assert "Email wajib diisi untuk pengiriman tiket." in errors
    assert "Nomor HP wajib diisi." in errors


def test_validate_manual_reservation_success():
    ok, errors = validate_manual_reservation(
        {"nama": "Budi", "email": "budi@test.com", "phone": "081234567890"}
    )
    assert ok is True
    assert errors == []
