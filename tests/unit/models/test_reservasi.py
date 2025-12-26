# tests/test_models/test_reservasi.py
from datetime import date, timedelta, time
from models import Reservasi, JadwalPemeriksaan, Dokter, Poliklinik


def _make_jadwal(db, jam_mulai=time(8, 0), jam_selesai=time(10, 0), kuota=10):
    poli = Poliklinik.create("Poli Umum", "desc")
    dokter = Dokter(nama_dokter="Dr Test", spesialisasi="Umum", poliklinik_id=poli.poliklinik_id)
    db.session.add(dokter)
    db.session.commit()

    jadwal = JadwalPemeriksaan(
        tanggal=date.today(),
        listjadwal_id=None,
        kuota=kuota,
        hari="Senin",
        dokter_id=dokter.dokter_id,
        poliklinik_id=poli.poliklinik_id,
        jam_mulai=jam_mulai,
        jam_selesai=jam_selesai,
    )
    db.session.add(jadwal)
    db.session.commit()
    return jadwal


# -------------------------
# get_upcoming_and_history
# -------------------------

def test_get_upcoming_and_history_splits_correctly(db):
    pasien_id = 1
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    jadwal = _make_jadwal(db)

    # upcoming: status Menunggu/Dikonfirmasi dan tanggal >= today :contentReference[oaicite:4]{index=4}
    Reservasi.create(pasien_id, jadwal.jadwal_id, 1, tomorrow, "Menunggu", False)
    Reservasi.create(pasien_id, jadwal.jadwal_id, 2, today, "Dikonfirmasi", False)

    # history: tanggal < today atau status bukan Menunggu/Dikonfirmasi
    Reservasi.create(pasien_id, jadwal.jadwal_id, 3, yesterday, "Menunggu", False)
    Reservasi.create(pasien_id, jadwal.jadwal_id, 4, today, "Selesai", False)

    upcoming, history = Reservasi.get_upcoming_and_history(pasien_id)

    assert len(upcoming) == 2
    assert len(history) == 2

    assert all(r.status in ["Menunggu", "Dikonfirmasi"] and r.tanggal_reservasi >= today for r in upcoming)


def test_get_upcoming_and_history_empty_returns_empty_lists(db):
    upcoming, history = Reservasi.get_upcoming_and_history(999)
    assert upcoming == []
    assert history == []


# -------------------------
# cancel_reservasi
# -------------------------

def test_cancel_reservasi_success(db):
    jadwal = _make_jadwal(db)
    reservasi, err = Reservasi.create(
        pasien_id=1,
        jadwal_id=jadwal.jadwal_id,
        no_urut=1,
        tanggal=date.today(),
        status="Menunggu",
        is_reminded=False,
    )
    assert err is None

    ok, msg = Reservasi.cancel_reservasi(reservasi.reservasi_id, pasien_id=1)
    assert ok is True
    assert msg is None

    db.session.refresh(reservasi)
    assert reservasi.status == "Dibatalkan"  # :contentReference[oaicite:5]{index=5}


def test_cancel_reservasi_not_found(db):
    ok, msg = Reservasi.cancel_reservasi("not-exist-id", pasien_id=1)
    assert ok is False
    assert msg == "Data reservasi tidak ditemukan."  # :contentReference[oaicite:6]{index=6}


def test_cancel_reservasi_wrong_owner(db):
    jadwal = _make_jadwal(db)
    reservasi, _ = Reservasi.create(
        pasien_id=1,
        jadwal_id=jadwal.jadwal_id,
        no_urut=1,
        tanggal=date.today(),
        status="Menunggu",
        is_reminded=False,
    )

    ok, msg = Reservasi.cancel_reservasi(reservasi.reservasi_id, pasien_id=2)
    assert ok is False
    assert msg == "Anda tidak memiliki akses untuk membatalkan reservasi ini."  # :contentReference[oaicite:7]{index=7}


def test_cancel_reservasi_blocked_by_status(db):
    jadwal = _make_jadwal(db)
    reservasi, _ = Reservasi.create(
        pasien_id=1,
        jadwal_id=jadwal.jadwal_id,
        no_urut=1,
        tanggal=date.today(),
        status="Selesai",
        is_reminded=False,
    )

    ok, msg = Reservasi.cancel_reservasi(reservasi.reservasi_id, pasien_id=1)
    assert ok is False
    assert msg == "Reservasi ini sudah tidak bisa dibatalkan."  # :contentReference[oaicite:8]{index=8}


# -------------------------
# estimasi_waktu
# -------------------------

def test_estimasi_waktu_computed_when_jadwal_exists(db):
    jadwal = _make_jadwal(db, jam_mulai=time(9, 0))
    reservasi, _ = Reservasi.create(
        pasien_id=1,
        jadwal_id=jadwal.jadwal_id,
        no_urut=3,  # (3-1)*20 = 40 menit => 09:40 :contentReference[oaicite:9]{index=9}
        tanggal=date.today(),
        status="Menunggu",
        is_reminded=False,
    )

    # akses property; harus terhitung
    assert reservasi.estimasi_waktu == "09:40"


def test_estimasi_waktu_fallback_when_relation_missing(db):
    # bikin reservasi tanpa bikin jadwal valid -> akses jadwalpemeriksaan akan error -> fallback :contentReference[oaicite:10]{index=10}
    reservasi, _ = Reservasi.create(
        pasien_id=1,
        jadwal_id="jadwal-tidak-ada",
        no_urut=1,
        tanggal=date.today(),
        status="Menunggu",
        is_reminded=False,
    )

    assert reservasi.estimasi_waktu == "Sesuai Antrian"
