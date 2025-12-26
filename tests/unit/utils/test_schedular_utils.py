from datetime import date, time
from flask import Flask


# dummy column object supaya ekspresi (col == value) aman dipakai
class _Col:
    def __init__(self, name="col"):
        self.name = name

    def __eq__(self, other):
        return True

    def __le__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __and__(self, other):
        return True

    def in_(self, values):
        # dipakai untuk ekspresi: col.in_([...])
        return True


def test_send_reminder_job_no_reservasi(monkeypatch):
    import utils.scheduler as sch

    app = Flask(__name__)

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return []

    # model dummy: harus punya atribut kolom yg dipakai di filter
    class R:
        query = FakeQuery()
        tanggal_reservasi = _Col("tanggal_reservasi")
        status = _Col("status")
        is_reminded = _Col("is_reminded")

    monkeypatch.setattr(sch, "Reservasi", R)

    called = {"sent": 0, "committed": 0}
    monkeypatch.setattr(sch.email, "send_mail", lambda msg: called.__setitem__("sent", called["sent"] + 1))
    monkeypatch.setattr(sch.db.session, "commit", lambda: called.__setitem__("committed", called["committed"] + 1))

    sch.send_reminder_job(app)

    assert called["sent"] == 0
    assert called["committed"] == 0  # return lebih awal kalau kosong


def test_send_reminder_job_sends_and_marks_reminded(monkeypatch):
    import utils.scheduler as sch

    app = Flask(__name__)

    class DummyDokter:
        nama_dokter = "Dr X"

    class DummyPoli:
        nama_poli = "Poli Umum"

    class DummyJadwal:
        dokter = DummyDokter()
        poliklinik = DummyPoli()
        jam_mulai = time(8, 0)

    class DummyPasien:
        nama = "Budi"
        email = "budi@test.com"

    class DummyReservasi:
        pasien = DummyPasien()
        jadwalpemeriksaan = DummyJadwal()
        tanggal_reservasi = date.today()
        status = "Menunggu"
        is_reminded = 0
        no_urut = 2

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return [DummyReservasi()]

    class R:
        query = FakeQuery()
        tanggal_reservasi = _Col("tanggal_reservasi")
        status = _Col("status")
        is_reminded = _Col("is_reminded")

    monkeypatch.setattr(sch, "Reservasi", R)

    called = {"sent": 0, "committed": 0}
    monkeypatch.setattr(sch.email, "send_mail", lambda msg: called.__setitem__("sent", called["sent"] + 1))
    monkeypatch.setattr(sch.db.session, "commit", lambda: called.__setitem__("committed", called["committed"] + 1))

    sch.send_reminder_job(app)

    assert called["sent"] == 1
    assert called["committed"] == 1


def test_process_generate_jadwal_raises_if_existing(monkeypatch):
    import utils.scheduler as sch

    app = Flask(__name__)

    class FakeJadwalQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return object()  # existing => harus raise

    class JP:
        query = FakeJadwalQuery()
        tanggal = _Col("tanggal")  # dipakai di filter

    monkeypatch.setattr(sch, "JadwalPemeriksaan", JP)

    try:
        sch._process_generate_jadwal(app, target_minggu="next")
        assert False, "Harusnya raise"
    except Exception as e:
        # pesan asli ada "SUDAH ADA", tapi kalau kamu ubah pesan di code,
        # setidaknya cek kata kunci ini lebih longgar:
        assert "SUDAH" in str(e).upper()


def test_process_generate_jadwal_creates_from_templates(monkeypatch):
    import utils.scheduler as sch

    app = Flask(__name__)

    class FakeJadwalQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class DummyTemplate:
        def __init__(self):
            self.hari = "Senin"
            self.jam_mulai = time(8, 0)
            self.jam_selesai = time(10, 0)  # 120 menit => kuota 12
            self.listjadwal_id = 1
            self.dokter_id = 10
            self.poliklinik_id = 20

    class FakeListJadwalQuery:
        def filter_by(self, **kwargs):
            # hari="Senin" => return 1 template, lainnya kosong
            self._hari = kwargs.get("hari")
            return self

        def all(self):
            return [DummyTemplate()] if self._hari == "Senin" else []

    created = {"count": 0, "last": None}

    def fake_create(**kwargs):
        created["count"] += 1
        created["last"] = kwargs
        return object(), None

    class JP:
        query = FakeJadwalQuery()
        tanggal = _Col("tanggal")
        create = staticmethod(fake_create)

    class LJ:
        query = FakeListJadwalQuery()

    monkeypatch.setattr(sch, "JadwalPemeriksaan", JP)
    monkeypatch.setattr(sch, "ListJadwal", LJ)

    committed = {"count": 0}
    monkeypatch.setattr(sch.db.session, "commit", lambda: committed.__setitem__("count", committed["count"] + 1))
    monkeypatch.setattr(sch.db.session, "rollback", lambda: None)

    count = sch._process_generate_jadwal(app, target_minggu="current")

    assert count == 1
    assert created["count"] == 1
    assert committed["count"] == 1
    assert created["last"]["kuota"] == 12
