from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime
from sqlalchemy.exc import IntegrityError # Untuk menangkap error database
from extensions import admin_required
from flask_login import current_user, login_required
from models import Reservasi, JadwalPemeriksaan, Pasien, ListJadwal, Poliklinik, Dokter, db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/')
@admin_required
def dashboard():
    return True


@admin_bp.route('/jadwal', methods=['GET'])
def manage_jadwal_dokter():
    dokters = Dokter.query.all()
    data_dokter = []
    
    for doc in dokters:
        jadwal_dict = {}
        # Mengambil data jadwal dokter
        for jadwal in doc.list_jadwal:
            # Pastikan format jam string HH:MM
            jam_str = f"{jadwal.jam_mulai.strftime('%H:%M')} - {jadwal.jam_selesai.strftime('%H:%M')}"
            jadwal_dict[jadwal.hari] = jam_str
            
        data_dokter.append({
            'id': doc.dokter_id,
            'name': doc.nama_dokter,
            'spec': doc.spesialisasi,
            'schedules': jadwal_dict
        })

    return render_template('jadwalDokter_admin.html', doctors=data_dokter)


@admin_bp.route('/admin/jadwal/save', methods=['GET','POST'])
@admin_required
def save_jadwal_dokter():
    try:
        data = request.get_json()
        doctor_id = data.get('doctor_id')
        schedules = data.get('schedule_list')

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'ID Dokter tidak ditemukan'}), 400

        # 1. Ambil Data Dokter
        dokter = Dokter.query.get(doctor_id)
        if not dokter:
            return jsonify({'status': 'error', 'message': 'Dokter tidak ditemukan di database'}), 404

        # 2. CARI POLIKLINIK ID BERDASARKAN SPESIALISASI DOKTER
        # Misal: Dokter Spesialis "Mata", cari di tabel Poliklinik yang namanya "Poli Mata" atau "Mata"
        nama_spesialisasi = dokter.spesialisasi
        
        poli = Poliklinik.query.filter(Poliklinik.nama_poli.ilike(f"%{nama_spesialisasi}%")).first()
        
        if poli:
            target_poli_id = poli.poliklinik_id
        else:
            poli_umum = Poliklinik.query.filter(Poliklinik.nama_poli.ilike("%Umum%")).first()
            if poli_umum:
                target_poli_id = poli_umum.poliklinik_id
            else:
                return jsonify({'status': 'error', 'message': f'Poliklinik untuk spesialis {nama_spesialisasi} belum terdaftar di database!'}), 500

        ListJadwal.query.filter_by(dokter_id=doctor_id).delete()

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
        return jsonify({'status': 'success', 'message': 'Jadwal berhasil diperbarui!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    
@admin_bp.route('/data-dokter', methods=['GET'])
def data_dokter():
    semua_dokter = Dokter.findAll()
    
    dokter_list = [d.to_dict() for d in semua_dokter]
    
    return render_template('admin_dataDokter.html', doctors=dokter_list, user=current_user)


@admin_bp.route('/data-dokter/add', methods=['POST'])
def add_dokter():
    return redirect(url_for('admin.data_dokter'))


@admin_bp.route('/data-dokter/delete/<int:id>', methods=['POST'])
def delete_dokter(id):
    return redirect(url_for('admin.data_dokter'))