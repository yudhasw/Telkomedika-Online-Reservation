from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
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
    

@admin_bp.route('/admin/jadwal/craete-jadwal', methods=['GET'])
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
    try:
        data = request.get_json()
        doctor_id = data.get('doctor_id')
        schedules = data.get('schedule_list')

        dokter = Dokter.query.get(doctor_id)
        if not dokter:
            return jsonify({'status': 'error', 'message': 'Dokter tidak ditemukan'}), 404

        nama_spesialisasi = dokter.spesialisasi
        poli = Poliklinik.query.filter(Poliklinik.nama_poli.ilike(f"%{nama_spesialisasi}%")).first()
        
        if poli:
            target_poli_id = poli.poliklinik_id
        else:
            poli_umum = Poliklinik.query.filter(Poliklinik.nama_poli.ilike("%Umum%")).first()
            target_poli_id = poli_umum.poliklinik_id if poli_umum else 1

        # Hapus FK listjadwal_id pada jadwalpemeriksaan untuk menghindari error db
        jadwal_lama = ListJadwal.query.filter_by(dokter_id=doctor_id).all()
        for jadwal in jadwal_lama:
            jp_terkait = JadwalPemeriksaan.query.filter_by(listjadwal_id=jadwal.listjadwal_id).all()
            for jp in jp_terkait:
                jp.listjadwal_id = None
            db.session.delete(jadwal)
        
        for item in schedules:
            try:
                jam_mulai = datetime.strptime(item['start'], '%H:%M').time()
                jam_selesai = datetime.strptime(item['end'], '%H:%M').time()
            except ValueError:
                continue

            new_jadwal = ListJadwal(
                dokter_id=doctor_id,
                poliklinik_id=target_poli_id,
                hari=item['day'],             
                jam_mulai=jam_mulai,
                jam_selesai=jam_selesai
            )
            db.session.add(new_jadwal)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Jadwal berhasil diperbarui!'})

    except Exception as e:
        db.session.rollback()
        print(f"Error Save: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/admin/jadwal/create-jadwal/generate-manual', methods=['POST'])
@admin_required
def generate_jadwal_manual():
    try:
        data = request.get_json() or {}
        scope = data.get('scope', 'next') 

        count = _process_generate_jadwal(target_minggu=scope)
        
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
    try:
        jadwal = JadwalPemeriksaan.query.get(id)
        
        if not jadwal:
            return jsonify({'status': 'error', 'message': 'Data tidak ditemukan'}), 404
            
        # VALIDASI PENTING: Cek apakah ada pasien reservasi?
        # Menggunakan relationship 'reservasi' yang ada di model JadwalPemeriksaan
        jumlah_reservasi = len(jadwal.reservasi)
        
        if jumlah_reservasi > 0:
            return jsonify({
                'status': 'error', 
                'message': f'Gagal Hapus! Terdapat {jumlah_reservasi} pasien yang sudah reservasi di jadwal ini. Silakan batalkan/pindahkan reservasi pasien terlebih dahulu.'
            }), 409
            
        db.session.delete(jadwal)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Jadwal berhasil dihapus.'})

    except Exception as e:
        db.session.rollback()
        # Print error ke terminal agar kita tahu penyebab aslinya jika masih error 500
        print(f"CRITICAL ERROR DELETE: {e}") 
        return jsonify({'status': 'error', 'message': f'Server Error: {str(e)}'}), 500


@admin_bp.route('/admin/jadwal/delete-week', methods=['POST'])
@admin_required
def delete_jadwal_week():
    try:
        data = request.get_json()
        scope = data.get('scope')
        
        today = date.today()
        
        if scope == 'current':
            start_date = today - timedelta(days=today.weekday())
            target_str = "Minggu Ini"
        else:
            days_to_monday = 0 - today.weekday()
            if days_to_monday <= 0: days_to_monday += 7
            start_date = today + timedelta(days=days_to_monday)
            target_str = "Minggu Depan"
            
        end_date = start_date + timedelta(days=6)
        
        deleted_count = JadwalPemeriksaan.query.filter(
            JadwalPemeriksaan.tanggal >= start_date,
            JadwalPemeriksaan.tanggal <= end_date
        ).delete()
        
        db.session.commit()
        
        if deleted_count == 0:
            return jsonify({'status': 'warning', 'message': f'Tidak ada jadwal yang dihapus untuk {target_str}.'})
            
        return jsonify({'status': 'success', 'message': f'Berhasil menghapus {deleted_count} jadwal untuk {target_str}.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/admin/jadwal/update', methods=['POST'])
@admin_required
def update_jadwal_item():
    try:
        data = request.get_json()
        id = data.get('id')
        jam_mulai_str = data.get('jam_mulai')
        jam_selesai_str = data.get('jam_selesai')
        kuota = data.get('kuota')
        
        jadwal = JadwalPemeriksaan.query.get(id)
        if not jadwal:
            return jsonify({'status': 'error', 'message': 'Data tidak ditemukan'}), 404
            
        # Update Data
        if jam_mulai_str:
            jadwal.jam_mulai = datetime.strptime(jam_mulai_str, '%H:%M').time()
        if jam_selesai_str:
            jadwal.jam_selesai = datetime.strptime(jam_selesai_str, '%H:%M').time()
        
        # Validasi Jam Terbalik
        if jadwal.jam_selesai <= jadwal.jam_mulai:
            return jsonify({'status': 'error', 'message': 'Jam Selesai tidak boleh lebih awal dari Jam Mulai'}), 400

        if kuota:
            jadwal.kuota = int(kuota)
        else:
            dummy_date = date.today()
            start_dt = datetime.combine(dummy_date, jadwal.jam_mulai)
            end_dt = datetime.combine(dummy_date, jadwal.jam_selesai)
            durasi = (end_dt - start_dt).total_seconds() / 60
            jadwal.kuota = int(durasi / 10)

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Jadwal berhasil diperbarui.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
# =========================================================
# ATUR DATA DOKTER (CRUD)
# =========================================================

@admin_bp.route('/admin/data-dokter', methods=['GET'])
@admin_required
def data_dokter():
    # Ambil semua data dokter
    dokters = Dokter.query.order_by(Dokter.nama_dokter.asc()).all()
    # Ambil data poliklinik untuk dropdown spesialisasi
    polis = Poliklinik.query.all()
    
    return render_template('admin_datadokter.html', dokters=dokters, polis=polis)

@admin_bp.route('/admin/data-dokter/add', methods=['POST'])
@admin_required
def add_dokter():
    try:
        data = request.get_json()
        nama = data.get('nama')
        poli_id = data.get('poli_id') # Ambil ID Poli
        
        # Validasi sederhana
        if not nama or not poli_id:
            return jsonify({'status': 'error', 'message': 'Nama dan Poli wajib diisi'}), 400
            
        # Ambil nama poli untuk disimpan di kolom string (backup)
        poli = Poliklinik.query.get(poli_id)
        nama_spesialisasi = poli.nama_poli if poli else "Umum"

        # Panggil method create yang baru
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
    try:
        data = request.get_json()
        
        # Ambil data dari frontend
        id = data.get('id')
        nama = data.get('nama')
        poli_id = data.get('poli_id') # Mengambil ID Poli
        
        # Validasi input sederhana
        if not id or not nama or not poli_id:
            return jsonify({'status': 'error', 'message': 'Data tidak lengkap (ID, Nama, dan Poli wajib diisi)'}), 400

        # Cari dokter yang akan diedit
        dokter = Dokter.query.get(id)
        if not dokter:
            return jsonify({'status': 'error', 'message': 'Dokter tidak ditemukan'}), 404
            
        # Cari Nama Poli berdasarkan ID untuk disimpan di kolom string 'spesialisasi'
        # (Ini menjaga agar kolom lama 'spesialisasi' tetap sinkron dengan relasi baru)
        poli = Poliklinik.query.get(poli_id)
        nama_spesialisasi = poli.nama_poli if poli else "Umum"

        # Lakukan Update ke Database
        dokter.nama_dokter = nama
        dokter.spesialisasi = nama_spesialisasi # Update string label
        dokter.poliklinik_id = poli_id          # Update Foreign Key relasi
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Data dokter berhasil diperbarui.'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error Update Dokter: {e}") # Print error di terminal untuk debugging
        return jsonify({'status': 'error', 'message': f'Gagal update: {str(e)}'}), 500

@admin_bp.route('/admin/data-dokter/delete/<int:id>', methods=['DELETE'])
@admin_required
def delete_dokter(id):
    try:
        dokter = Dokter.query.get(id)
        if not dokter:
            return jsonify({'status': 'error', 'message': 'Dokter tidak ditemukan'}), 404
        
        # Cek apakah dokter punya jadwal aktif (Foreign Key Check)
        if len(dokter.list_jadwal) > 0:
             return jsonify({'status': 'error', 'message': 'Gagal hapus: Dokter ini masih memiliki jadwal praktek. Hapus jadwalnya terlebih dahulu.'}), 409

        db.session.delete(dokter)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Data dokter berhasil dihapus.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500