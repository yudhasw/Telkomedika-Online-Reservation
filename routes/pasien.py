from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from flask_mail import Message
from models import Reservasi, JadwalPemeriksaan, Pasien, ListJadwal
from datetime import date
from extensions import mail

pasien_bp = Blueprint("pasien", __name__)


@pasien_bp.route("/home")
@login_required
def homepage():
    try:
        pasien = current_user
        return render_template('home.html', pasien=pasien)
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "danger")
        return render_template('home.html', pasien=pasien)


@pasien_bp.route("/profile")
@login_required
def profile():
    pasien = current_user
    
    if request.method == 'POST':
        try:
            Pasien.create(
                nama='',
                email='',
                password='',
                nomor_hp='',
                jenis_kelamin='',
                tanggal_lahir=''
            )
        except Exception as e:
            flash(f"Terjadi kesalahan: {e}", "danger")

    return render_template('profile.html', pasien=pasien)


@pasien_bp.route("/form-administrasi", methods=['GET', 'POST'])
@login_required
def form_administrasi():
    pasien = current_user

    if request.method == 'POST':
        jadwal_id = request.form.get('jadwal_id')

        if not jadwal_id:
            flash('Silakan pilih jadwal terlebih dahulu.', 'warning')
            return render_template('pasien/form_administrasi.html', pasien=pasien)

        try:
            no_urut = nomorUrut(jadwal_id)
        except Exception as e:
            current_app.logger.error(f"Gagal mendapatkan nomor urut: {e}")
            flash('Terjadi kesalahan saat mengambil nomor antrian.', 'danger')
            return render_template('pasien/form_administrasi.html', pasien=pasien)

        if not no_urut:
            flash('Jadwal penuh.', 'warning')
            return render_template('pasien/form_administrasi.html', pasien=pasien)

        reservasi, msg = Reservasi.create(
            pasien_id=pasien.pasien_id,
            jadwal_id=jadwal_id,
            no_urut=no_urut,
            tanggal=date.today(),
            status='Menunggu'
        )

        if msg:
            flash(f"Terjadi kesalahan saat membuat reservasi: {msg}", "danger")
            return render_template('pasien/form_administrasi.html', pasien=pasien)

        try:
            notifikasiReservasi(pasien, reservasi)
        except Exception as e:
            current_app.logger.error(f"Gagal mengirim email reservasi: {e}")
            flash("Reservasi berhasil dibuat, tetapi email notifikasi gagal dikirim.", "warning")

        flash("Reservasi berhasil dibuat.", "success")
        return redirect(url_for('pasien_bp.homepage'))

    return render_template('pasien/form_administrasi.html', pasien=pasien)


def nomorUrut(jadwal_id):
    jadwal = JadwalPemeriksaan.query.get(jadwal_id)
    current_nomor_urut = JadwalPemeriksaan.query.filter_by(
        tanggal=jadwal.tanggal, 
        listjadwal_id=jadwal.listjadwal_id
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

@pasien_bp.route('/jadwal-dokter')
def jadwal_dokter():
    list_jadwal = ListJadwal.get_data()

    return render_template('jadwalDokter.html', data=list_jadwal)


