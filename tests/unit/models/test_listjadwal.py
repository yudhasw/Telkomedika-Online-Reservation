# tests/test_models/test_listjadwal.py
from datetime import date, time
from models import ListJadwal, Dokter, Poliklinik, JadwalPemeriksaan


def _make_poli(db, nama):
    poli = Poliklinik.create(nama_poli=nama, deskripsi="desc")
    return poli


def _make_dokter(db, poli_id, spesialisasi):
    dokter = Dokter(nama_dokter="Dr Test", spesialisasi=spesialisasi, poliklinik_id=poli_id)
    db.session.add(dokter)
    db.session.commit()
    return dokter


def _make_listjadwal(db, dokter_id, poli_id, hari="Senin"):
    lj = ListJadwal(
        dokter_id=dokter_id,
        poliklinik_id=poli_id,
        hari=hari,
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
    )
    db.session.add(lj)
    db.session.commit()
    return lj


def _make_jadwal_pemeriksaan_linked(db, dokter_id, poli_id, listjadwal_id):
    jp = JadwalPemeriksaan(
        tanggal=date.today(),
        listjadwal_id=listjadwal_id,
        kuota=5,
        hari="Senin",
        dokter_id=dokter_id,
        poliklinik_id=poli_id,
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
    )
    db.session.add(jp)
    db.session.commit()
    return jp


def test_update_all_doctor_not_found(db):
    ok, msg = ListJadwal.update_all(doctor_id=999999, schedules=[])
    assert ok is False
    assert msg == "Dokter tidak ditemukan"


def test_update_all_success_deletes_old_and_unlinks_jadwalpemeriksaan(db):
    # setup poli (match spesialisasi) + poli umum (fallback)
    poli_gigi = _make_poli(db, "Poli Gigi")
    poli_umum = _make_poli(db, "Poli Umum")

    # dokter spesialisasi = "Gigi", akan match ke "Poli Gigi" via ilike %Gigi% :contentReference[oaicite:4]{index=4}
    dokter = _make_dokter(db, poli_id=poli_gigi.poliklinik_id, spesialisasi="Gigi")

    # buat jadwal lama + jadwal pemeriksaan yang terhubung ke jadwal lama
    jadwal_lama = _make_listjadwal(db, dokter.dokter_id, poli_gigi.poliklinik_id, hari="Senin")
    jp = _make_jadwal_pemeriksaan_linked(db, dokter.dokter_id, poli_gigi.poliklinik_id, jadwal_lama.listjadwal_id)

    assert ListJadwal.query.filter_by(dokter_id=dokter.dokter_id).count() == 1
    assert jp.listjadwal_id == jadwal_lama.listjadwal_id

    # update dengan schedules baru
    schedules = [
        {"day": "Rabu", "start": "09:00", "end": "11:00"},
        {"day": "Jumat", "start": "13:00", "end": "15:00"},
    ]
    ok, msg = ListJadwal.update_all(dokter.dokter_id, schedules)
    assert ok is True
    assert msg is None

    # jadwal lama harus terhapus
    assert ListJadwal.query.filter_by(dokter_id=dokter.dokter_id, hari="Senin").count() == 0

    # JP yang tadinya terkait harus diputus relasinya (jadi None) :contentReference[oaicite:5]{index=5}
    db.session.refresh(jp)
    assert jp.listjadwal_id is None

    # jadwal baru harus ada 2
    new_rows = ListJadwal.query.filter_by(dokter_id=dokter.dokter_id).all()
    assert len(new_rows) == 2

    # semua jadwal baru harus pakai target_poli_id yang sesuai (Poli Gigi)
    assert all(r.poliklinik_id == poli_gigi.poliklinik_id for r in new_rows)


def test_update_all_skips_invalid_time_items(db):
    poli_umum = _make_poli(db, "Poli Umum")
    dokter = _make_dokter(db, poli_id=poli_umum.poliklinik_id, spesialisasi="TidakCocok")

    schedules = [
        {"day": "Senin", "start": "xx:yy", "end": "10:00"},  # invalid => harus di-skip :contentReference[oaicite:6]{index=6}
        {"day": "Selasa", "start": "08:00", "end": "10:00"}, # valid
    ]

    ok, msg = ListJadwal.update_all(dokter.dokter_id, schedules)
    assert ok is True
    assert msg is None

    rows = ListJadwal.query.filter_by(dokter_id=dokter.dokter_id).all()
    assert len(rows) == 1
    assert rows[0].hari == "Selasa"
