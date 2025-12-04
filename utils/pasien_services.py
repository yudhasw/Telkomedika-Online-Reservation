from flask import current_app
from flask_mail import Message
from models import Reservasi, JadwalPemeriksaan
from extensions import mail
from datetime import datetime, timedelta, date


def nomorUrut(jadwal_id):
    jadwal = JadwalPemeriksaan.query.get(jadwal_id)
    current_nomor_urut = Reservasi.query.filter_by(
        jadwal_id=jadwal_id
    ).count()
    if current_nomor_urut < jadwal.kuota:
        return current_nomor_urut+1
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
    jadwal_reservasi = pasien.get("tanggal_reservasi")

    try:
        jam_mulai_dokter = reservasi.jadwalpemeriksaan.listjadwal.jam_mulai
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
        f"Tanggal       : {jadwal_reservasi.strftime('%d-%m-%Y')}\n"
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