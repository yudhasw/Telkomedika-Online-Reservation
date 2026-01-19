from datetime import date, time
from models import JadwalPemeriksaan, Reservasi, Dokter, Poliklinik

def _make_poli_dokter(db):
    poli = Poliklinik.create(nama_poli="Poli Umum", deskripsi="desc")
    dokter = Dokter(nama_dokter="Dr Test", spesialisasi="Umum", poliklinik_id=poli.poliklinik_id)
    db.session.add(dokter)
    db.session.commit()
    return poli, dokter

def _make_jadwal(db, kuota=5):
    poli, dokter = _make_poli_dokter(db)
    jadwal = JadwalPemeriksaan(
        tanggal=date.today(),
        listjadwal_id=None,
        kuota=kuota,
        hari="Senin",
        dokter_id=dokter.dokter_id,
        poliklinik_id=poli.poliklinik_id,
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
    )
    db.session.add(jadwal)
    db.session.commit()
    return jadwal

# -------------------------
# get_sisa_kuota
# -------------------------

def test_get_sisa_kuota_when_none_returns_0(db):
    jadwal = _make_jadwal(db, kuota=10)
    assert jadwal.get_sisa_kuota(None) == 0  # :contentReference[oaicite:2]{index=2}

def test_get_sisa_kuota_invalid_str_returns_0(db):
    jadwal = _make_jadwal(db, kuota=10)
    assert jadwal.get_sisa_kuota("not-a-date") == 0  # :contentReference[oaicite:3]{index=3}

def test_get_sisa_kuota_decreases_with_reservasi_count(db):
    jadwal = _make_jadwal(db, kuota=3)
    target = date.today()

    # isi 2 reservasi untuk jadwal yang sama pada tanggal yang sama
    r1 = Reservasi(pasien_id=1, jadwal_id=jadwal.jadwal_id, no_urut=1, tanggal_reservasi=target, status="Menunggu")
    r2 = Reservasi(pasien_id=2, jadwal_id=jadwal.jadwal_id, no_urut=2, tanggal_reservasi=target, status="Menunggu")
    db.session.add_all([r1, r2])
    db.session.commit()

    assert jadwal.get_sisa_kuota(target) == 1  # 3 - 2


# -------------------------
# update
# -------------------------

def test_update_rejects_end_before_start(db):
    jadwal = _make_jadwal(db, kuota=5)

    ok, msg = jadwal.update("10:00", "09:00", None)  # jam selesai lebih awal :contentReference[oaicite:4]{index=4}
    assert ok is False
    assert msg == "Jam Selesai tidak boleh lebih awal dari Jam Mulai"

def test_update_sets_manual_kuota_when_given(db):
    jadwal = _make_jadwal(db, kuota=5)

    ok, msg = jadwal.update("08:00", "10:00", 12)
    assert ok is True
    assert msg is None
    assert jadwal.kuota == 12

def test_update_auto_calculates_kuota_when_none(db):
    jadwal = _make_jadwal(db, kuota=1)

    # durasi 60 menit => kuota = 60/10 = 6 :contentReference[oaicite:5]{index=5}
    ok, msg = jadwal.update("08:00", "09:00", None)
    assert ok is True
    assert msg is None
    assert jadwal.kuota == 6
