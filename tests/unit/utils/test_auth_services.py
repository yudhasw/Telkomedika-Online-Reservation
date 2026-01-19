import pytest

from utils.auth_services import (
    validate_password_strength,
    validate_register,
    send_otp_email,
)
from models import Pasien, db


def test_validate_password_strength_success():
    ok, err = validate_password_strength("Abcdef1!", "Abcdef1!")
    assert ok is True
    assert err is None


@pytest.mark.parametrize(
    "password,confirm,expected_msg",
    [
        ("", "", "Password tidak boleh kosong."),
        ("Ab1!", "Ab1!", "Password minimal 8 karakter."),
        ("abcdefg!", "abcdefg!", "Password harus mengandung minimal 1 angka."),
        ("abcdefg1!", "abcdefg1!", "Password harus mengandung huruf kapital."),
        ("ABCDEFG1!", "ABCDEFG1!", "Password harus mengandung huruf kecil."),
        ("Abcdefg12", "Abcdefg12", "Password harus mengandung minimal 1 simbol unik (!@#$%)."),
        ("Abcdef1!", "Abcdef1?", "Konfirmasi password tidak cocok."),
    ],
)
def test_validate_password_strength_failures(password, confirm, expected_msg):
    ok, err = validate_password_strength(password, confirm)
    assert ok is False
    assert err == expected_msg


def test_validate_register_success(app, db):
    # tidak ada pasien lain dengan email tsb
    data = {
        "nama": "Yudha",
        "email": "yudha@test.com",
        "nomor_hp": "081234567890",
        "tanggal_lahir": "2000-01-01",
        "jenis_kelamin": "Laki-laki",
        "password": "Abcdef1!",
        "confirm_password": "Abcdef1!",
    }

    ok, errors, cleaned = validate_register(data)
    assert ok is True
    assert all(v is None for v in errors.values())
    assert cleaned["email"] == "yudha@test.com"


def test_validate_register_duplicate_email(app, db):
    # seed pasien existing
    p = Pasien(
        nama="A",
        email="dup@test.com",
        password_hash="hash",
        nomor_hp="081234567890",
    )
    db.session.add(p)
    db.session.commit()

    data = {
        "nama": "Budi",
        "email": "dup@test.com",  # duplicate
        "nomor_hp": "081234567891",
        "tanggal_lahir": "2000-01-01",
        "jenis_kelamin": "Laki-laki",
        "password": "Abcdef1!",
        "confirm_password": "Abcdef1!",
    }

    ok, errors, cleaned = validate_register(data)
    assert ok is False
    assert errors["email"] == "Email sudah digunakan."


def test_send_otp_email_calls_send_mail(monkeypatch):
    sent = {"called": False, "msg": None}

    def fake_send_mail(msg):
        sent["called"] = True
        sent["msg"] = msg

    # patch utils.email.send_mail yang dipanggil auth_services.send_otp_email
    import utils.auth_services as auth_services_module
    monkeypatch.setattr(auth_services_module.email, "send_mail", fake_send_mail)

    ok = send_otp_email("target@test.com", "123456", kategori="reset")
    assert ok is True
    assert sent["called"] is True
    assert sent["msg"] is not None
    # minimal cek recipient & body berisi otp
    assert "target@test.com" in sent["msg"].recipients
    assert "123456" in (sent["msg"].body or "")
