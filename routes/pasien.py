import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import Reservasi, JadwalPemeriksaan, Pasien, ListJadwal, Poliklinik, Dokter, db
from datetime import date, datetime, timedelta
from utils import pasien_services, auth_services
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
    
    data = {
        "nama": request.form.get('nama'),
        "email": request.form.get('email'),
        "nomor_hp": request.form.get('nomor_hp'),
        "jenis_kelamin": request.form.get('jenis_kelamin'),
        "tanggal_lahir": request.form.get('tanggal_lahir')
    }
    is_valid, errors, cleaned_data = pasien_services.validate_profile_update(data, current_user.pasien_id)

    if not is_valid:
        for err_msg in errors.values():
            if err_msg:
                flash(f"{err_msg}", "danger")
        
        return redirect(url_for('pasien.profile', tab='edit'))
    try:
        pasien.nama = cleaned_data['nama']
        pasien.nomor_hp = cleaned_data['phone']
        pasien.jenis_kelamin = cleaned_data['jenis_kelamin']
        pasien.tanggal_lahir = cleaned_data['tgl_lahir']

        new_email = cleaned_data['email']

        if new_email != pasien.email:
            otp_code = str(random.randint(1000, 9999))
  
            session['pending_new_email'] = new_email
            session['change_email_otp'] = otp_code
            session['change_email_expired'] = (datetime.now() + timedelta(minutes=2)).timestamp()
            
            if auth_services.send_otp_email(new_email, otp_code, 'register'): 
                db.session.commit()
                
                flash("Kami mengirimkan kode verifikasi ke email baru Anda. Mohon verifikasi untuk menyimpan perubahan email.", "info")
                return redirect(url_for('auth.verify_email_change'))
            else:
                db.session.rollback()
                flash("Gagal mengirim kode verifikasi ke email baru.", "danger")
                return redirect(url_for('pasien.profile', tab='edit'))
        
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

    strong, err_msg = auth_services.validate_password_strength(new_pass, conf_pass)

    if not strong:
        flash(err_msg, 'danger')
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
            "phone"  : request.form.get('nomor_hp'),
            "tanggal_pelayanan"  : request.form.get('tanggal_pelayanan'),
            "tanggal_reservasi"  : request.form.get('tanggal_pelayanan'),
        }

        is_valid, error_list = pasien_services.validate_manual_reservation(data_pasien)

        if not is_valid:
            for err in error_list:
                if err:
                    flash(err, 'danger')
            return render_template('reservasi.html', pasien=pasien, jadwal=jadwal, poli_id=poli_id, tanggal=tanggal_str)

        if not jadwal_id:
            flash('Silakan pilih jadwal terlebih dahulu.', 'warning')
            return render_template('reservasi.html', pasien=pasien, jadwal=jadwal, poli_id=poli_id, tanggal=tanggal_str)
        
        try:
            tanggal_fix = datetime.strptime(data_pasien.get("tanggal_reservasi"), '%Y-%m-%d').date()
        except ValueError:
            flash("Format tanggal tidak valid.", "danger")
            return redirect(url_for('pasien.form_reservasi'))

        try:
            no_urut = pasien_services.nomorUrut(jadwal_id, tanggal_fix)
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
            tanggal=tanggal_fix, 
            status='Menunggu',
            is_reminded=0
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
    list_jadwal = JadwalPemeriksaan.get_all_data()

    return render_template('lihatjadwal.html', data=list_jadwal, get_next_date=pasien_services.get_next_date)