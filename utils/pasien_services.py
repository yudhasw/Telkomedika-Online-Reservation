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
    if not getattr(pasien, "email", None):
        current_app.logger.warning(
            f"Pasien {pasien.pasien_id} tidak punya email, email tidak dikirim."
        )
        return

    subject = "Konfirmasi Reservasi Pemeriksaan"
    recipients = [pasien.email]

    msg = Message(subject=subject, recipients=recipients)

    msg.body = (
        f"Halo {pasien.nama},\n\n"
        f"Reservasi Anda telah berhasil dibuat.\n"
        f"ID Reservasi : {reservasi.reservasi_id}\n"
        f"Tanggal      : {reservasi.tanggal.strftime('%d-%m-%Y')}\n"
        f"No Antrian   : {reservasi.no_urut}\n"
        f"Status       : {reservasi.status}\n\n"
        f"Silakan datang sesuai jadwal.\n"
        f"Terima kasih."
    )

    msg.html = f"""
        <p>Halo <b>{pasien.nama}</b>,</p>
        <p>Reservasi Anda telah <b>berhasil dibuat</b> dengan detail:</p>
        <ul>
            <li>ID Reservasi: <b>{reservasi.reservasi_id}</b></li>
            <li>Tanggal: <b>{reservasi.tanggal_reservasi.strftime('%d-%m-%Y')}</b></li>
            <li>No Antrian: <b>{reservasi.no_urut}</b></li>
            <li>Status: <b>{reservasi.status}</b></li>
        </ul>
        <p>Silakan datang sesuai jadwal. Terima kasih.</p>
    """

    mail.send(msg)