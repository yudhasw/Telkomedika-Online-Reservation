# tests/test_models/test_dokter.py
from models import Dokter, Poliklinik
from datetime import time


def test_dokter_create_success(db):
    ok, msg = Dokter.create(nama="Dr A", spesialis="Poli Gigi", poli_id=None)
    assert ok is True
    assert msg is not None

    dokter = Dokter.query.filter_by(nama_dokter="Dr A").first()
    assert dokter is not None
    assert dokter.spesialisasi == "Poli Gigi"


def test_dokter_update_success_set_spesialisasi_from_poli(db):
    poli = Poliklinik.create(nama_poli="Poli Anak", deskripsi="desc")

    ok, _ = Dokter.create(nama="Dr Old", spesialis="Umum", poli_id=None)
    assert ok is True
    dokter = Dokter.query.filter_by(nama_dokter="Dr Old").first()
    assert dokter is not None

    ok, err = Dokter.update(dokter.dokter_id, nama="Dr New", poli_id=poli.poliklinik_id)
    assert ok is True
    assert err is None

    db.session.refresh(dokter)
    assert dokter.nama_dokter == "Dr New"
    assert dokter.poliklinik_id == poli.poliklinik_id
    assert dokter.spesialisasi == "Poli Anak"  # diambil dari nama_poli :contentReference[oaicite:2]{index=2}


def test_dokter_update_not_found(db):
    poli = Poliklinik.create(nama_poli="Poli Umum", deskripsi="desc")

    ok, err = Dokter.update(999999, nama="Dr X", poli_id=poli.poliklinik_id)
    assert ok is False
    assert err == "Dokter tidak ditemukan"  # :contentReference[oaicite:3]{index=3}


def test_dokter_update_poli_not_found_sets_umum(db):
    # buat dokter
    ok, _ = Dokter.create(nama="Dr A", spesialis="Awal", poli_id=None)
    assert ok is True
    dokter = Dokter.query.filter_by(nama_dokter="Dr A").first()
    assert dokter is not None

    # poli_id yang tidak ada => Poliklinik.query.get None => spesialisasi jadi "Umum" :contentReference[oaicite:4]{index=4}
    ok, err = Dokter.update(dokter.dokter_id, nama="Dr A Updated", poli_id=999999)
    assert ok is True
    assert err is None

    db.session.refresh(dokter)
    assert dokter.nama_dokter == "Dr A Updated"
    assert dokter.spesialisasi == "Umum"

def test_dokter_delete_success_when_no_jadwal(db):
    dokter = Dokter(nama_dokter="Dr Hapus", spesialisasi="X", poliklinik_id=None)
    db.session.add(dokter)
    db.session.commit()

    ok, err = dokter.delete()
    assert ok is True
    assert err is None

    assert Dokter.query.get(dokter.dokter_id) is None
