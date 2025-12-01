from flask import current_app
from flask_mail import Message
from models import Reservasi, JadwalPemeriksaan
from extensions import mail


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

    msg = Message(subject=subject, recipients=recipients)

    msg.body = (
        f"Halo {nama_pasien},\n\n"
        f"Reservasi Anda telah berhasil dibuat.\n"
        f"ID Reservasi : {reservasi.reservasi_id}\n"
        f"Tanggal      : {jadwal_reservasi.strftime('%d-%m-%Y')}\n"
        f"No Antrian   : {reservasi.no_urut}\n"
        f"Status       : {reservasi.status}\n\n"
        f"Silakan datang minimal 5 menit sebelum jadwal.\n"
        f"Terima kasih."
    )

    msg.html = f"""
        <p>Halo <b>{nama_pasien}</b>,</p>
        <p>Reservasi Anda telah <b>berhasil dibuat</b> dengan detail:</p>
        <ul>
            <li>ID Reservasi: <b>{reservasi.reservasi_id}</b></li>
            <li>Tanggal: <b>{jadwal_reservasi.strftime('%d-%m-%Y')}</b></li>
            <li>No Antrian: <b>{reservasi.no_urut}</b></li>
            <li>Status: <b>{reservasi.status}</b></li>
        </ul>
        <p>Silakan datang minimal 5 menit sebelum jadwal. Terima kasih.</p>
    """
    
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Gagal mengirim email: {e}")
        raise e