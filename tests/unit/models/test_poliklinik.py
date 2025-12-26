# tests/test_models/test_poliklinik.py
from datetime import time
from models import Poliklinik, Dokter, ListJadwal


def test_poliklinik_create_success(db):
    poli = Poliklinik.create("Poli Test", "desc")
    assert poli is not None
    assert poli.poliklinik_id is not None
    assert poli.nama_poli == "Poli Test"


def test_poliklinik_get_all_data_returns_list_or_none(db):
    # awalnya kosong
    assert Poliklinik.get_all_data() is None

    Poliklinik.create("Poli 1", "desc")
    data = Poliklinik.get_all_data()
    assert data is not None
    assert len(data) >= 1


def test_poliklinik_delete_blocked_when_has_doctor(db):
    poli = Poliklinik.create("Poli Anak", "desc")

    dokter = Dokter(
        nama_dokter="Dr A",
        spesialisasi="Anak",
        poliklinik_id=poli.poliklinik_id,
    )
    db.session.add(dokter)
    db.session.commit()

    ok, msg, code = poli.delete()
    assert ok is False
    assert code == 409
    assert "Masih ada 1 dokter" in msg  # pesan mengandung jumlah dokter :contentReference[oaicite:3]{index=3}


def test_poliklinik_delete_blocked_when_has_listjadwal(db):
    poli_target = Poliklinik.create("Poli Target", "desc")
    poli_lain = Poliklinik.create("Poli Lain", "desc")

    # dokter ditempatkan di poli lain => poli_target.dokter_list = []
    dokter = Dokter(
        nama_dokter="Dr B",
        spesialisasi="Umum",
        poliklinik_id=poli_lain.poliklinik_id,
    )
    db.session.add(dokter)
    db.session.commit()

    # ListJadwal mengacu ke poli_target => poli_target.list_jadwal terisi
    lj = ListJadwal(
        jam_mulai=time(8, 0),
        jam_selesai=time(10, 0),
        dokter_id=dokter.dokter_id,
        poliklinik_id=poli_target.poliklinik_id,
        hari="Senin",
    )
    db.session.add(lj)
    db.session.commit()

    ok, msg, code = poli_target.delete()
    assert ok is False
    assert code == 409
    assert msg == "Masih ada template jadwal yang menggunakan poli ini."


def test_poliklinik_delete_success_when_no_relations(db):
    poli = Poliklinik.create("Poli Kosong", "desc")

    ok, msg, code = poli.delete()
    assert ok is True
    assert msg is None
    assert code is None

    assert Poliklinik.query.get(poli.poliklinik_id) is None
