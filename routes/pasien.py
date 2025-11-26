from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from models import Reservasi, JadwalPemeriksaan, Pasien
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


@pasien_bp.route("/jadwal-dokter")
@login_required
def jadwalDokter():
    pasien = current_user

    poli_id = request.args.get('poli_id')
    tanggal_str = request.args.get('tanggal')

    # QUERY DASAR TANPA FILTER POLI DAN TANGGAL
    query_filter_Jadwal = JadwalPemeriksaan.query.filter(JadwalPemeriksaan.tanggal >= date.today())

    if poli_id:
        query_filter_Jadwal = query_filter_Jadwal.filter(JadwalPemeriksaan.poli_id == poli_id)

    if tanggal_str:
        tanggal = date.strptime(tanggal_str, '%Y-%m-%d').date()
        query_filter_Jadwal = query_filter_Jadwal.filter(JadwalPemeriksaan.tanggal == tanggal)

    # SORTING JADWAL SESUAI WAKTU (listjadwal)
    jadwal = query_filter_Jadwal.order_by(JadwalPemeriksaan.listjadwal_id.asc()).all()

    return render_template('jadwal.html', jadwal=jadwal)


@pasien_bp.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    pasien = current_user

    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        nomor_hp = request.form.get('nomor_hp')
        jenis_kelamin = request.form.get('jenis_kelamin')
        tanggal_lahir = request.form.get('tanggal_lahir')

        try:
            pasien.nama = nama or pasien.nama
            pasien.email = email or pasien.email
            pasien.nomor_hp = nomor_hp or pasien.nomor_hp
            pasien.jenis_kelamin = jenis_kelamin or pasien.jenis_kelamin
            pasien.tanggal_lahir = tanggal_lahir or pasien.tanggal_lahir

            db.session.commit()
            flash("Profil berhasil diperbarui.", "success")
            return redirect(url_for('pasien.homepage'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating profile: {e}")
            flash(f"Terjadi kesalahan: {e}", "danger")

    return render_template('profile.html', pasien=pasien)


@pasien_bp.route("/changepassword", methods=['GET', 'POST'])
@login_required
def profile_updatepassword():
    pasien = current_user

    if request.method == 'POST':
        old_password = request.form.get('old-password')
        new_password = request.form.get('password')
        confirm_password = request.form.get('conf-password')

        if not new_password:
            flash("Password baru kosong.", "warning")
            return render_template('changepassword.html', pasien=pasien)

        if new_password != confirm_password: 
            flash("Password tidak sama!", 'warning')
            return render_template('changepassword.html', pasien=pasien)

        if not check_password_hash(pasien.password, old_password):
            flash("Password lama salah.", "warning")
            return render_template('changepassword.html', pasien=pasien)

        try:
            pasien.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Password berhasil diperbarui.", "success")
            return redirect(url_for('pasien.profile'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating password: {e}")
            flash(f"Terjadi kesalahan: {e}", "danger")

    return render_template('profile_updatepassword.html', pasien=pasien)


@pasien_bp.route("/form-reservasi", methods=['GET', 'POST'])
@login_required
def form_reservasi():
    pasien = current_user

    poli_id = request.args.get('poli_id')
    tanggal_str = request.args.get('tanggal')

    # QUERY DASAR TANPA FILTER POLI DAN TANGGAL
    query_filter_Jadwal = JadwalPemeriksaan.query.filter(JadwalPemeriksaan.tanggal >= date.today())

    if poli_id:
        query_filter_Jadwal = query_filter_Jadwal.filter(JadwalPemeriksaan.poli_id == poli_id)

    if tanggal_str:
        tanggal = date.strptime(tanggal_str, '%Y-%m-%d').date()
        query_filter_Jadwal = query_filter_Jadwal.filter(JadwalPemeriksaan.tanggal == tanggal)

    # SORTING JADWAL SESUAI WAKTU (listjadwal)
    jadwal = query_filter_Jadwal.order_by(JadwalPemeriksaan.listjadwal_id.asc()).all()


    if request.method == 'POST':
        jadwal_id = request.form.get('jadwal_id')

        if not jadwal_id:
            flash('Silakan pilih jadwal terlebih dahulu.', 'warning')
            return render_template(
                'reservasi.html', 
                pasien=pasien, 
                jadwal=jadwal, 
                poli_id=poli_id, 
                tanggal=tanggal_str
            )

        # AMBIL NOMOR URUT
        try:
            no_urut = nomorUrut(jadwal_id)
        except Exception as e:
            current_app.logger.error(f"Gagal mendapatkan nomor urut: {e}")
            flash('Terjadi kesalahan saat mengambil nomor antrian.', 'danger')
            return render_template(
                'reservasi.html', 
                pasien=pasien, 
                jadwal=jadwal, 
                poli_id=poli_id, 
                tanggal=tanggal_str
            )

        if not no_urut:
            flash('Jadwal penuh.', 'warning')
            return render_template(
                'reservasi.html', 
                pasien=pasien, 
                jadwal=jadwal, 
                poli_id=poli_id, 
                tanggal=tanggal_str
            )

        # BUAT RESERVASI
        reservasi, msg = Reservasi.create(
            pasien_id=pasien.pasien_id,
            jadwal_id=jadwal_id,
            no_urut=no_urut,
            tanggal=date.today(),
            status='Menunggu'
        )

        if msg:
            flash(f"Terjadi kesalahan saat membuat reservasi: {msg}", "danger")
            return render_template(
                'reservasi.html', 
                pasien=pasien, 
                jadwal=jadwal, 
                poli_id=poli_id, 
                tanggal=tanggal_str
            )
        
        # KIRIM NOTIFIKASI EMAIL RESERVASI BERHASIL
        try:
            notifikasiReservasi(pasien, reservasi)
        except Exception as e:
            current_app.logger.error(f"Gagal mengirim email reservasi: {e}")
            flash("Reservasi berhasil dibuat, tetapi email notifikasi gagal dikirim.", "warning")

        flash("Reservasi berhasil dibuat.", "success")
        return redirect(url_for('pasien_bp.homepage'))


    return render_template(
        'reservasi.html', 
        pasien=pasien, 
        jadwal=jadwal, 
        poli_id=poli_id, 
        tanggal=tanggal_str
    )


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

