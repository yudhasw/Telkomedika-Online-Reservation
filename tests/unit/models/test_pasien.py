# tests/test_models/test_pasien.py
from datetime import date
from werkzeug.security import generate_password_hash
from models import Pasien


def test_pasien_create_success(db):
    pasien, err = Pasien.create(
        nama="Yudha",
        email="yudha@test.com",
        password_hash=generate_password_hash("secret"),
        nomor_hp="08123456789",
        jenis_kelamin="Laki-laki",
        tanggal_lahir=date(2003, 1, 1),
    )

    assert err is None
    assert pasien is not None
    assert pasien.pasien_id is not None
    assert pasien.email == "yudha@test.com"


def test_pasien_create_duplicate_email_should_fail(db):
    # insert pertama
    pasien1, err1 = Pasien.create(
        nama="A",
        email="dup@test.com",
        password_hash=generate_password_hash("secret"),
        nomor_hp=None,
        jenis_kelamin=None,
        tanggal_lahir=None,
    )
    assert err1 is None
    assert pasien1 is not None

    # insert kedua: email sama => harus gagal (unique constraint)
    pasien2, err2 = Pasien.create(
        nama="B",
        email="dup@test.com",
        password_hash=generate_password_hash("secret2"),
        nomor_hp=None,
        jenis_kelamin=None,
        tanggal_lahir=None,
    )

    assert pasien2 is None
    assert err2 is not None  # biasanya berisi pesan IntegrityError/unique constraint


def test_verify_password_true_and_false(db):
    pasien, err = Pasien.create(
        nama="A",
        email="pw@test.com",
        password_hash=generate_password_hash("mypassword"),
        nomor_hp=None,
        jenis_kelamin=None,
        tanggal_lahir=None,
    )
    assert err is None

    assert pasien.verify_password("mypassword") is True
    assert pasien.verify_password("wrong") is False


def test_set_password_plain_success(db):
    pasien, err = Pasien.create(
        nama="A",
        email="setpw@test.com",
        password_hash=generate_password_hash("oldpass"),
        nomor_hp=None,
        jenis_kelamin=None,
        tanggal_lahir=None,
    )
    assert err is None

    old_hash = pasien.password_hash

    ok, msg = pasien.set_password_plain("newpass")
    assert ok is True
    assert msg is None

    assert pasien.password_hash != old_hash
    assert pasien.verify_password("newpass") is True
    assert pasien.verify_password("oldpass") is False


def test_authenticate_success(db):
    pasien, err = Pasien.create(
        nama="A",
        email="auth@test.com",
        password_hash=generate_password_hash("secret"),
        nomor_hp=None,
        jenis_kelamin=None,
        tanggal_lahir=None,
    )
    assert err is None

    user = Pasien.authenticate("auth@test.com", "secret")
    assert user is not None
    assert user.pasien_id == pasien.pasien_id


def test_authenticate_wrong_password_returns_none(db):
    Pasien.create(
        nama="A",
        email="auth2@test.com",
        password_hash=generate_password_hash("secret"),
        nomor_hp=None,
        jenis_kelamin=None,
        tanggal_lahir=None,
    )

    user = Pasien.authenticate("auth2@test.com", "wrong")
    assert user is None


def test_authenticate_email_not_found_returns_none(db):
    user = Pasien.authenticate("notfound@test.com", "secret")
    assert user is None


def test_apply_profile_update_updates_fields_and_returns_email(db):
    pasien, err = Pasien.create(
        nama="Old",
        email="profile@test.com",
        password_hash=generate_password_hash("secret"),
        nomor_hp="0800",
        jenis_kelamin="Laki-laki",
        tanggal_lahir=date(2000, 1, 1),
    )
    assert err is None

    cleaned = {
        "nama": "New Name",
        "phone": "081234",
        "jenis_kelamin": "Perempuan",
        "tgl_lahir": date(2002, 2, 2),
        "email": "profile@test.com",  # method kamu return email dari cleaned_data
    }

    returned_email = pasien.apply_profile_update(cleaned)

    assert returned_email == "profile@test.com"
    assert pasien.nama == "New Name"
    assert pasien.nomor_hp == "081234"
    assert pasien.jenis_kelamin == "Perempuan"
    assert pasien.tanggal_lahir == date(2002, 2, 2)
