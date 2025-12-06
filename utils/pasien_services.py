import re
from flask import current_app
from flask_mail import Message
from models import Reservasi, JadwalPemeriksaan
from extensions import mail
from datetime import datetime, timedelta, date
from models import Admin, Pasien


def nomorUrut(jadwal_id, tanggal_pelayanan):
    jadwal = JadwalPemeriksaan.query.get(jadwal_id)
    
    if not jadwal:
        return None

    current_nomor_urut = Reservasi.query.filter_by(
        jadwal_id=jadwal_id,
        tanggal_reservasi=tanggal_pelayanan 
    ).count()

    if current_nomor_urut < jadwal.kuota:
        return current_nomor_urut + 1
    
    return None

def notifikasiReservasi(pasien, reservasi):
    email_tujuan = pasien.get("email")
    if not email_tujuan:
        current_app.logger.warning(
            f"Data Pasien tidak punya email, email tidak dikirim."
        )
        return

    subject = "Konfirmasi Reservasi Pemeriksaan"
    recipients = [email_tujuan]

    nama_pasien = pasien.get("nama", "Pasien")
    jadwal_reservasi = reservasi.tanggal_reservasi

    try:
        jam_mulai_dokter = reservasi.jadwalpemeriksaan.jam_mulai
        waktu_start_praktek = datetime.combine(jadwal_reservasi, jam_mulai_dokter)

        hasil_estimasi = waktu_start_praktek + timedelta(minutes=((reservasi.no_urut - 1) * 20))
        perkiraan_waktu = hasil_estimasi.strftime("%H:%M")

    except Exception as e:
        current_app.logger.error(f"Gagal menghitung estimasi waktu: {e}")
        perkiraan_waktu = "Sesuai Jadwal Praktek"

    msg = Message(subject=subject, recipients=recipients)
    msg.body = (
        f"Halo {nama_pasien},\n\n"
        f"Reservasi Anda telah berhasil dibuat.\n"
        f"ID Reservasi  : {reservasi.reservasi_id}\n"
        f"Tanggal       : {jadwal_reservasi}\n"
        f"No Antrian    : {reservasi.no_urut}\n"
        f"Status        : {reservasi.status}\n"
        f"Perkiraan Jam : {reservasi.status}\n\n"
        f"Silakan datang minimal 15 menit sebelum jadwal.\n"
        f"Terima kasih."
    )

    msg.html = f"""
        <p>Halo <b>{nama_pasien}</b>,</p>
        <p>Reservasi Anda telah <b>berhasil dibuat</b> dengan detail:</p>
        <ul>
            <li>ID Reservasi: <b>{reservasi.reservasi_id}</b></li>
            <li>Tanggal: <b>{jadwal_reservasi.strftime('%d-%m-%Y')}</b></li>
            <li>No Antrian: <b>{reservasi.no_urut}</b></li>
            <li>Perkiraan Dilayani: <b>{perkiraan_waktu} WIB</b></li>
            <li>Status: <b>{reservasi.status}</b></li>
        </ul>
        <p><i>*Waktu di atas adalah estimasi. Mohon datang 15 menit lebih awal.</i></p>
        <p>Terima kasih telah menggunakan layanan kami.</p>
    """
    
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Gagal mengirim email: {e}")

def get_next_date(hari_target):
    days_map = {'Senin': 0, 'Selasa': 1, 'Rabu': 2, 'Kamis': 3, 'Jumat': 4, 'Sabtu': 5, 'Minggu': 6}
    
    today = date.today()
    target_day_idx = days_map.get(hari_target, 0)
    current_day_idx = today.weekday()
    
    days_ahead = target_day_idx - current_day_idx
    
    if days_ahead <= 0: 
        days_ahead += 7
        
    next_date = today + timedelta(days=days_ahead)
    return next_date.strftime('%Y-%m-%d')

def validate_profile_update(data, current_user_id):
    errors = {
        "nama": None,
        "email": None,
        "phone": None,
        "tanggal_lahir": None,
        "jenis_kelamin": None
    }

    cleaned = {
        "nama": (data.get("nama") or "").strip(),
        "email": (data.get("email") or "").strip(),
        "phone": (data.get("nomor_hp") or ""),
        "tgl_lahir": (data.get("tanggal_lahir") or ""),
        "jenis_kelamin": (data.get("jenis_kelamin") or ""),
    }

    nama = cleaned["nama"]
    if not nama:
        errors["nama"] = "Nama tidak boleh kosong."
    elif len(nama) < 3:
        errors["nama"] = "Nama minimal 3 karakter."

    email = cleaned["email"]
    if not email:
        errors["email"] = "Email tidak boleh kosong."
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = "Format email tidak valid."
    else:
        existing_user = Pasien.query.filter_by(email=email).first()
        if existing_user and existing_user.pasien_id != current_user_id:
            errors["email"] = "Email sudah digunakan oleh pengguna lain."

    phone = cleaned["phone"]
    if not phone:
        errors["phone"] = "Nomor Hp tidak boleh kosong."
    else:
        phone = phone.strip().replace(" ", "").replace("-", "")
        cleaned["phone"] = phone

        if not re.match(r"^(08\d{8,13}|\+628\d{7,12})$", phone):
            errors["phone"] = "Format nomor HP tidak valid (contoh: 0812...)"
        elif re.search(r"[A-Za-z]", phone):
            errors["phone"] = "Nomor HP harus berupa angka"

    if not cleaned["tgl_lahir"]:
        errors["tanggal_lahir"] = "Tanggal lahir wajib diisi."
    
    if not cleaned["jenis_kelamin"]:
        errors["jenis_kelamin"] = "Jenis kelamin wajib dipilih."

    if any(value is not None for value in errors.values()):
        return False, errors, cleaned
    
    return True, errors, cleaned

def validate_manual_reservation(data):

    errors = []

    nama = (data.get("nama") or "").strip()
    if not nama:
        errors.append("Nama pasien wajib diisi.")
    elif len(nama) < 3:
        errors.append("Nama pasien minimal 3 karakter.")

    email = (data.get("email") or "").strip()
    if not email:
        errors.append("Email wajib diisi untuk pengiriman tiket.")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("Format email tidak valid.")

    phone = (data.get("phone") or "").strip().replace(" ", "").replace("-", "")
    if not phone:
        errors.append("Nomor HP wajib diisi.")
    elif not re.match(r"^(08\d{8,13}|\+628\d{7,12})$", phone):
        errors.append("Format nomor HP tidak valid (Gunakan 08xx atau +628xx).")
    elif re.search(r"[A-Za-z]", phone):
        errors.append("Nomor HP harus berupa angka.")

    if errors:
        return False, errors
    
    return True, []