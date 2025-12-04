from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import Reservasi, JadwalPemeriksaan, Pasien, ListJadwal, Poliklinik, Dokter, db
from datetime import date
from utils import pasien_services
from extensions import pasien_required


pasien_bp = Blueprint("pasien", __name__)


@pasien_bp.route("/home")
@pasien_required
def homepage():
    try:
        pasien = current_user
        return render_template('dashboard.html', pasien=pasien)
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "danger")
        return render_template('dashboard.html', pasien=pasien)


@pasien_bp.route("/profile", methods=['GET'])
@pasien_required
def profile():
    try:
        data_reservasi = Reservasi.get_reservation_data(current_user.pasien_id)
    except Exception as e:
        current_app.logger.error(f"Error fetching reservation: {e}")
        data_reservasi = []

    upcoming = []
    history = []
    today = date.today()

    if data_reservasi:
        for res in data_reservasi:
            if res.status in ['Menunggu', 'Dikonfirmasi'] and res.tanggal_reservasi >= today:
                upcoming.append(res)
            else:
                history.append(res)
    return render_template('profile.html',upcoming=upcoming, pasien=current_user, history=history)


@pasien_bp.route("/profile/edit", methods=['POST'])
@pasien_required
def profile_edit():
    pasien = Pasien.query.get(current_user.pasien_id)
    
    nama = request.form.get('nama')
    email = request.form.get('email')
    nomor_hp = request.form.get('nomor_hp')
    jenis_kelamin = request.form.get('jenis_kelamin')
    tanggal_lahir = request.form.get('tanggal_lahir')

    try:
        pasien.nama = nama
        pasien.email = email
        pasien.nomor_hp = nomor_hp
        pasien.jenis_kelamin = jenis_kelamin
        pasien.tanggal_lahir = tanggal_lahir
        
        db.session.commit()
        flash("Profil berhasil diperbarui.", "success")
        
        return redirect(url_for('pasien.profile', tab='profile'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Gagal update profil: {e}")
        flash("Gagal memperbarui profil. Silakan coba lagi.", "danger")
        
        return redirect(url_for('pasien.profile', tab='edit'))


@pasien_bp.route("/profile/change-password", methods=['POST'])
@pasien_required
def profile_updatepassword():
    pasien = Pasien.query.get(current_user.pasien_id)
    
    old_pass = request.form.get('old-password')
    new_pass = request.form.get('password')
    conf_pass = request.form.get('conf-password')

    if not check_password_hash(pasien.password_hash, old_pass):
        flash("Password lama salah.", "danger")
        return redirect(url_for('pasien.profile', tab='password'))

    if new_pass != conf_pass:
        flash("Konfirmasi password tidak cocok.", "danger")
        return redirect(url_for('pasien.profile', tab='password'))
        
    if len(new_pass) < 8:
        flash("Password baru minimal 8 karakter.", "danger")
        return redirect(url_for('pasien.profile', tab='password'))

    try:
        pasien.password_hash = generate_password_hash(new_pass)
        db.session.commit()
        
        flash("Password berhasil diubah. Silakan login ulang jika diperlukan.", "success")
        return redirect(url_for('pasien.profile', tab='password'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Gagal ubah password: {e}")
        flash("Terjadi kesalahan sistem.", "danger")
        return redirect(url_for('pasien.profile', tab='password'))


@pasien_bp.route("/form-reservasi", methods=['GET', 'POST'])
@pasien_required
def form_reservasi():
    pasien = current_user

    poli_id = request.args.get('poli_id')
    tanggal_str = request.args.get('tanggal')
    jadwal = []

    if tanggal_str:
        jadwal = JadwalPemeriksaan.get_filtered_data(poli_id, tanggal_str)

    if request.method == 'POST':
        jadwal_id = request.form.get('jadwal_id')
        data_pasien = {
            "nama"  : request.form.get('nama'),
            "email"  : request.form.get('email'),
            "phone"  : request.form.get('telepon'),
            "tanggal_pelayanan"  : request.form.get('tanggal-pelayanan'),
            "tanggal_reservasi"  : date.today(),
        }

        if not jadwal_id:
            flash('Silakan pilih jadwal terlebih dahulu.', 'warning')
            return render_template('reservasi.html', pasien=pasien, jadwal=jadwal, poli_id=poli_id, tanggal=tanggal_str)

        try:
            no_urut = pasien_services.nomorUrut(jadwal_id) 
        except Exception as e:
            current_app.logger.error(f"Gagal mendapatkan nomor urut: {e}")
            flash('Terjadi kesalahan sistem saat mengambil nomor antrian.', 'danger')
            return render_template('reservasi.html', pasien=pasien, jadwal=jadwal, poli_id=poli_id, tanggal=tanggal_str)

        if not no_urut:
            flash('Mohon maaf, Kuota untuk jadwal ini sudah penuh.', 'warning')
            return render_template('reservasi.html', pasien=pasien, jadwal=jadwal, poli_id=poli_id, tanggal=tanggal_str)

        reservasi, msg = Reservasi.create(
            pasien_id=pasien.pasien_id,
            jadwal_id=jadwal_id,
            no_urut=no_urut,
            tanggal=date.today(), 
            status='Menunggu'
        )

        if msg:
            flash(f"Gagal membuat reservasi: {msg}", "danger")
            return render_template('reservasi.html', pasien=pasien, jadwal=jadwal, poli_id=poli_id, tanggal=tanggal_str)
        
        try:
            pasien_services.notifikasiReservasi(data_pasien, reservasi)
        except Exception as e:
            current_app.logger.error(f"Gagal mengirim email: {e}")
            flash("Reservasi berhasil, namun notifikasi email gagal terkirim.", "warning")

        flash("Reservasi berhasil dibuat! Silakan cek riwayat.", "success")
        return redirect(url_for('pasien.homepage'))

    return render_template(
        'reservasi.html', 
        pasien=pasien, 
        jadwal=jadwal, 
        poli_id=poli_id, 
        tanggal=tanggal_str
    )

@pasien_bp.route("/reservasi/cancel/<string:reservasi_id>", methods=['POST'])
@pasien_required
def batalkan_reservasi(reservasi_id):
    reservasi = Reservasi.query.get(reservasi_id)
 
    if not reservasi:
        flash("Data reservasi tidak ditemukan.", "danger")
        return redirect(url_for('pasien.profile', tab='tickets'))
  
    if reservasi.pasien_id != current_user.pasien_id:
        flash("Anda tidak memiliki akses untuk membatalkan reservasi ini.", "danger")
        return redirect(url_for('pasien.profile', tab='tickets'))

    if reservasi.status in ['Selesai', 'Dibatalkan', 'Dalam Proses']:
        flash("Reservasi ini sudah tidak bisa dibatalkan.", "warning")
        return redirect(url_for('pasien.profile', tab='tickets'))

    success, err_msg = reservasi.set_status('Dibatalkan')
    if success:
        flash("Reservasi berhasil dibatalkan.", "success")
    else:
        current_app.logger.error(f"Gagal membatalkan reservasi: {err_msg}")
        flash("Terjadi kesalahan sistem saat membatalkan reservasi.", "danger")

    return redirect(url_for('pasien.profile', tab='tickets'))

@pasien_bp.route('/jadwal-dokter')
def jadwal_dokter():
    list_jadwal = ListJadwal.get_data()

    return render_template('lihatjadwal.html', data=list_jadwal, get_next_date=pasien_services.get_next_date)


