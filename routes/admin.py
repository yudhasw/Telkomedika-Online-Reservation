from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError
from extensions import admin_required
from flask_login import current_user, login_required
from models import Reservasi, JadwalPemeriksaan, Pasien, ListJadwal, Poliklinik, Dokter, db
from utils.scheduler import _process_generate_jadwal

admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/admin')
@admin_required
def dashboard():
    total_dokter = Dokter.query.count()
    return render_template('admin_dashboard.html', admin=current_user, total_dokter=total_dokter)

# =========================================================
# ATUR JADWAL PEMERIKSAAN DAN TEMPLATE JADWAL
# =========================================================

@admin_bp.route('/admin/jadwal', methods=['GET'])
@admin_required
def jadwal():
    today = date.today()

    start_week_1 = today - timedelta(days=today.weekday())
    end_week_1 = start_week_1 + timedelta(days=6)
    
    start_week_2 = end_week_1 + timedelta(days=1)
    end_week_2 = start_week_2 + timedelta(days=6)
    
    jadwal_ini = JadwalPemeriksaan.query.filter(
        JadwalPemeriksaan.tanggal >= start_week_1,
        JadwalPemeriksaan.tanggal <= end_week_1
    ).order_by(JadwalPemeriksaan.tanggal.asc(), JadwalPemeriksaan.jam_mulai.asc()).all()

    jadwal_depan = JadwalPemeriksaan.query.filter(
        JadwalPemeriksaan.tanggal >= start_week_2,
        JadwalPemeriksaan.tanggal <= end_week_2
    ).order_by(JadwalPemeriksaan.tanggal.asc(), JadwalPemeriksaan.jam_mulai.asc()).all()

    label_ini = f"{start_week_1.strftime('%d %b')} - {end_week_1.strftime('%d %b %Y')}"
    label_depan = f"{start_week_2.strftime('%d %b')} - {end_week_2.strftime('%d %b %Y')}"

    return render_template(
        'admin_jadwal.html',
        jadwal_ini=jadwal_ini,
        jadwal_depan=jadwal_depan,
        label_ini=label_ini,
        label_depan=label_depan
    )
    

@admin_bp.route('/admin/jadwal/create-jadwal', methods=['GET'])
@admin_required
def create_jadwal():
    dokters = Dokter.query.all()
    data_dokter = []
    
    for doc in dokters:
        jadwal_dict = {}

        for jadwal in doc.list_jadwal:
            jam_str = f"{jadwal.jam_mulai.strftime('%H:%M')} - {jadwal.jam_selesai.strftime('%H:%M')}"
            jadwal_dict[jadwal.hari] = jam_str
            
        data_dokter.append({
            'id': doc.dokter_id,
            'name': doc.nama_dokter,
            'spec': doc.spesialisasi,
            'schedules': jadwal_dict
        })

    return render_template('admin_createjadwal.html', doctors=data_dokter)

    
@admin_bp.route('/admin/jadwal/create-jadwal/save', methods=['POST'])
@admin_required
def save_jadwal():
    data = request.get_json() or {}
    doctor_id = data.get('doctor_id')
    schedules = data.get('schedule_list') or []

    success, msg = ListJadwal.update_all(doctor_id, schedules)

    if not success:
        if msg == "Dokter tidak ditemukan":
            return jsonify({'status': 'error', 'message': msg}), 404
        return jsonify({'status': 'error', 'message': msg}), 500

    return jsonify({'status': 'success', 'message': 'Jadwal berhasil diperbarui!'})


@admin_bp.route('/admin/jadwal/create-jadwal/generate-manual', methods=['POST'])
@admin_required
def generate_jadwal_manual():
    try:
        data = request.get_json() or {}
        scope = data.get('scope', 'next')
        real_app = current_app._get_current_object()

        count = _process_generate_jadwal(real_app, target_minggu=scope)
        
        waktu_str = "Minggu Ini" if scope == 'current' else "Minggu Depan"
        
        if count == 0:
            return jsonify({
                'status': 'warning',
                'message': f'Proses selesai, namun 0 jadwal dibuat untuk {waktu_str}. Kemungkinan Anda belum mengisi/menyimpan "Template Jadwal" (kotak putih di tabel).'
            }), 409 
            
        return jsonify({
            'status': 'success', 
            'message': f'Berhasil! {count} jadwal baru telah ditambahkan untuk {waktu_str}.'
        })
        
    except Exception as e:
        error_msg = str(e)
        
        if "SUDAH ADA" in error_msg:
            return jsonify({
                'status': 'warning', 
                'message': f'{error_msg} Tidak ada data baru yang dibuat.'
            }), 409 
            
        print(f"Error Manual Generate: {e}")
        return jsonify({'status': 'error', 'message': f'Gagal: {error_msg}'}), 500
    

@admin_bp.route('/admin/jadwal/delete/<string:id>', methods=['DELETE'])
@admin_required
def delete_jadwal_item(id):
    success, msg = JadwalPemeriksaan.delete_one(id)

    if not success:
        if msg == "Data tidak ditemukan":
            return jsonify({'status': 'error', 'message': msg}), 404
        if msg.startswith("Terdapat"):
            return jsonify({'status': 'error', 'message': f'Gagal Hapus! {msg} Silakan batalkan/pindahkan reservasi pasien terlebih dahulu.'}), 409
        return jsonify({'status': 'error', 'message': f'Server Error: {msg}'}), 500

    return jsonify({'status': 'success', 'message': 'Jadwal berhasil dihapus.'})


@admin_bp.route('/admin/jadwal/delete-week', methods=['POST'])
@admin_required
def delete_jadwal_week():
    data = request.get_json() or {}
    scope = data.get('scope')

    deleted_count, err = JadwalPemeriksaan.delete_week(scope)

    if err:
        return jsonify({'status': 'error', 'message': err}), 500

    target_str = "Minggu Ini" if scope == 'current' else "Minggu Depan"

    if deleted_count == 0:
        return jsonify({'status': 'warning', 'message': f'Tidak ada jadwal yang dihapus untuk {target_str}.'})

    return jsonify({'status': 'success', 'message': f'Berhasil menghapus {deleted_count} jadwal untuk {target_str}.'})


@admin_bp.route('/admin/jadwal/update', methods=['POST'])
@admin_required
def update_jadwal_item():
    data = request.get_json() or {}
    id = data.get('id')
    jam_mulai_str = data.get('jam_mulai')
    jam_selesai_str = data.get('jam_selesai')
    kuota = data.get('kuota')

    jadwal = JadwalPemeriksaan.query.get(id)
    if not jadwal:
        return jsonify({'status': 'error', 'message': 'Data tidak ditemukan'}), 404

    success, msg = jadwal.update(jam_mulai_str, jam_selesai_str, kuota)

    if not success:
        return jsonify({'status': 'error', 'message': msg}), 400 if "Jam Selesai" in msg else 500

    return jsonify({'status': 'success', 'message': 'Jadwal berhasil diperbarui.'})

    
# =========================================================
# ATUR DATA DOKTER (CRUD)
# =========================================================

@admin_bp.route('/admin/data-dokter', methods=['GET'])
@admin_required
def data_dokter():
    dokters = Dokter.query.order_by(Dokter.nama_dokter.asc()).all()
    polis = Poliklinik.query.all()
    
    return render_template('admin_dataDokter.html', dokters=dokters, polis=polis)


@admin_bp.route('/admin/data-dokter/add', methods=['POST'])
@admin_required
def add_dokter():
    try:
        data = request.get_json()
        nama = data.get('nama')
        poli_id = data.get('poli_id')
        
        if not nama or not poli_id:
            return jsonify({'status': 'error', 'message': 'Nama dan Poli wajib diisi'}), 400

        poli = Poliklinik.query.get(poli_id)
        nama_spesialisasi = poli.nama_poli if poli else "Umum"

        success, msg = Dokter.create(nama, nama_spesialisasi, poli_id)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Berhasil menambahkan dokter baru.'})
        else:
            return jsonify({'status': 'error', 'message': msg}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/admin/data-dokter/update', methods=['POST'])
@admin_required
def update_dokter():
    data = request.get_json() or {}

    id = data.get('id')
    nama = data.get('nama')
    poli_id = data.get('poli_id') 

    if not id or not nama or not poli_id:
        return jsonify({'status': 'error', 'message': 'Data tidak lengkap (ID, Nama, dan Poli wajib diisi)'}), 400

    success, msg = Dokter.update(id, nama, poli_id)
    if not success:
        if msg == "Dokter tidak ditemukan":
            return jsonify({'status': 'error', 'message': msg}), 404
        return jsonify({'status': 'error', 'message': f'Gagal update: {msg}'}), 500

    return jsonify({'status': 'success', 'message': 'Data dokter berhasil diperbarui.'})



@admin_bp.route('/admin/data-dokter/delete/<int:id>', methods=['DELETE'])
@admin_required
def delete_dokter(id):
    dokter = Dokter.query.get(id)
    if not dokter:
        return jsonify({'status': 'error', 'message': 'Dokter tidak ditemukan'}), 404

    success, msg = dokter.delete()
    if not success:
        if "masih memiliki jadwal" in msg:
            return jsonify({'status': 'error', 'message': msg}), 409
        return jsonify({'status': 'error', 'message': msg}), 500

    return jsonify({'status': 'success', 'message': 'Data dokter berhasil dihapus.'})



# =========================================================
# ATUR DATA POLIKLINIK (CRUD)
# =========================================================

@admin_bp.route('/admin/data-poliklinik', methods=['GET'])
@admin_required
def data_poli():
    polis = Poliklinik.query.order_by(Poliklinik.nama_poli.asc()).all()
    return render_template('admin_dataPoliklinik.html', polis=polis)


@admin_bp.route('/admin/data-poliklinik/add', methods=['POST'])
@admin_required
def add_poli():
    try:
        data = request.get_json()
        nama = data.get('nama')
        deskripsi = data.get('deskripsi')
        
        if not nama:
            return jsonify({'status': 'error', 'message': 'Nama Poliklinik wajib diisi'}), 400

        cek_ada = Poliklinik.query.filter(Poliklinik.nama_poli.ilike(nama)).first()
        if cek_ada:
            return jsonify({'status': 'error', 'message': 'Nama Poliklinik sudah ada.'}), 400

        new_poli = Poliklinik(nama_poli=nama, deskripsi=deskripsi)
        db.session.add(new_poli)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Berhasil menambahkan Poliklinik baru.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/admin/data-poliklinik/update', methods=['POST'])
@admin_required
def update_poli():
    try:
        data = request.get_json()
        id = data.get('id')
        nama = data.get('nama')
        deskripsi = data.get('deskripsi')
        
        poli = Poliklinik.query.get(id)
        if not poli:
            return jsonify({'status': 'error', 'message': 'Poliklinik tidak ditemukan'}), 404
            
        poli.nama_poli = nama
        poli.deskripsi = deskripsi
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Data Poliklinik berhasil diperbarui.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/admin/data-poliklinik/delete/<int:id>', methods=['DELETE'])
@admin_required
def delete_poli(id):
    poli = Poliklinik.query.get(id)
    if not poli:
        return jsonify({'status': 'error', 'message': 'Poliklinik tidak ditemukan'}), 404

    success, msg, code = poli.delete()
    if not success:
        return jsonify({'status': 'error', 'message': f'Gagal hapus: {msg}'}), code or 500

    return jsonify({'status': 'success', 'message': 'Data Poliklinik berhasil dihapus.'})


# =========================================================
# MANAJEMEN RESERVASI PASIEN
# =========================================================

@admin_bp.route('/admin/data-reservasi', methods=['GET'])
@admin_required
def reservasi_list():
    status_filter = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')

    query = Reservasi.query

    if status_filter != 'all':
        query = query.filter(Reservasi.status == status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Reservasi.tanggal_reservasi == filter_date)
        except ValueError:
            pass

    reservasi_data = query.order_by(Reservasi.tanggal_reservasi.asc(), Reservasi.created_at.desc() if hasattr(Reservasi, 'created_at') else Reservasi.reservasi_id.asc()).all()

    return render_template(
        'admin_reservasi.html', 
        reservasi_list=reservasi_data,
        current_status=status_filter,
        current_date=date_filter,
    )

@admin_bp.route('/admin/reservasi/update-status', methods=['POST'])
@admin_required
def update_reservasi_status():
    data = request.get_json() or {}
    reservasi_id = data.get('id')
    new_status = data.get('status')

    reservasi = Reservasi.query.get(reservasi_id)
    if not reservasi:
        flash('Reservasi tidak ditemukan', 'danger')
        return jsonify({'status': 'error', 'message': 'Reservasi tidak ditemukan'}), 404

    success, msg = reservasi.update_status(new_status)

    if not success:
        flash(msg, 'danger')
        return jsonify({'status': 'error', 'message': msg}), 500

    flash(f'Status berhasil diubah menjadi {new_status}', 'success')
    return jsonify({'status': 'success', 'message': f'Status berhasil diubah menjadi {new_status}'})


@admin_bp.route('/admin/reservasi/delete/<string:reservasi_id>', methods=['DELETE'])
@admin_required
def delete_reservasi(reservasi_id):
    reservasi = Reservasi.query.get(reservasi_id)
    if not reservasi:
        flash("Data reservasi tidak ditemukan", 'danger')
        return jsonify({'status': 'error', 'message': 'Data reservasi tidak ditemukan'}), 404

    success, msg = reservasi.delete()
    if not success:
        flash(msg, 'danger')
        return jsonify({'status': 'error', 'message': msg}), 500

    flash("Data reservasi berhasil dihapus permanen.", 'success')
    return jsonify({'status': 'success', 'message': 'Data reservasi berhasil dihapus permanen.'})
