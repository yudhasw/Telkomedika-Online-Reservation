from datetime import datetime, timedelta, date
from extensions import mail, Message
from models import Reservasi, db, ListJadwal, JadwalPemeriksaan
from flask import current_app

def send_reminder_job(app):
    with app.app_context(): 

        besok = date.today() + timedelta(days=1)

        reservasi_list = Reservasi.query.filter(
            Reservasi.tanggal_reservasi == besok,
            Reservasi.status.in_(['Menunggu', 'Dikonfirmasi']),
            Reservasi.is_reminded == 0
        ).all()

        if not reservasi_list:
            return


        for res in reservasi_list:
            if res.pasien and res.pasien.email:
                try:
                    subject = f"Pengingat: Jadwal Pemeriksaan Besok ({res.tanggal_reservasi})"
                    
                    msg = Message(
                        subject=subject,
                        sender="telkomedikahealth@gmail.com",
                        recipients=[res.pasien.email]
                    )
                    
                    dokter_nama = res.jadwalpemeriksaan.listjadwal.dokter.nama_dokter
                    poli_nama = res.jadwalpemeriksaan.listjadwal.poliklinik.nama_poli
                    jadwal_reservasi = res.tanggal_reservasi

                    try:
                        jam_mulai_dokter = res.jadwalpemeriksaan.listjadwal.jam_mulai
                        waktu_start_praktek = datetime.combine(jadwal_reservasi, jam_mulai_dokter)

                        hasil_estimasi = waktu_start_praktek + timedelta(minutes=((res.no_urut - 1) * 20))
                        perkiraan_waktu = hasil_estimasi.strftime("%H:%M")

                    except Exception as e:
                        current_app.logger.error(f"Gagal menghitung estimasi waktu: {e}")
                        perkiraan_waktu = "Sesuai Jadwal Praktek"

                    msg.body = f"""
                    Halo {res.pasien.nama},
                    
                    Ini adalah pengingat untuk jadwal pemeriksaan kesehatan Anda BESOK.
                    
                    Dokter  : {dokter_nama}
                    Poli    : {poli_nama}
                    Tanggal : {res.tanggal_reservasi}
                    Jam     : {perkiraan_waktu}
                    Antrian : {res.no_urut}
                    
                    Mohon datang 10 menit lebih awal. Terima kasih.
                    """
                    
                    mail.send(msg)
     
                    res.is_reminded = 1
                except Exception as e:
                    print(f"Gagal kirim ke {res.pasien.email}: {e}")

        db.session.commit()
        

def _process_generate_jadwal(target_minggu):
    with current_app.app_context():
        today = date.today()
        
        if target_minggu == 'current':
            start_date = today - timedelta(days=today.weekday())
            label = "MANUAL: MINGGU INI"
        else:
            days_to_monday = 0 - today.weekday()
            if days_to_monday <= 0:
                days_to_monday += 7
            start_date = today + timedelta(days=days_to_monday)
            label = "MANUAL/AUTO: MINGGU DEPAN"

        end_date = start_date + timedelta(days=6)
        
        existing_data = JadwalPemeriksaan.query.filter(
            JadwalPemeriksaan.tanggal >= start_date,
            JadwalPemeriksaan.tanggal <= end_date
        ).first()
        
        print(f"\n=== [START] {label} ===")
        print(f"    Mulai Tanggal: {start_date}")
        
        if existing_data:
            pesan_error = (f"Jadwal untuk periode {start_date} s/d {end_date} "
                           f"SUDAH ADA. Harap hapus jadwal lama terlebih dahulu.")
            print(f"    [ABORT] {pesan_error}")
            raise Exception(pesan_error)
        
        hari_map = {
            0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 
            4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'
        }

        count_created = 0
        
        try:
            for i in range(7):
                current_date = start_date + timedelta(days=i)
                nama_hari = hari_map[current_date.weekday()]
                
                templates = ListJadwal.query.filter_by(hari=nama_hari).all()
                
                if not templates:
                    continue

                for template in templates:
                    # Validasi jam terbalik
                    if template.jam_selesai <= template.jam_mulai:
                        continue

                    dummy_date = date.today()
                    start_dt = datetime.combine(dummy_date, template.jam_mulai)
                    end_dt = datetime.combine(dummy_date, template.jam_selesai)
                    
                    durasi = end_dt - start_dt
                    total_menit = durasi.total_seconds() / 60
                    kuota_otomatis = int(total_menit / 10)

                    new_jadwal, error_msg = JadwalPemeriksaan.create(
                        tanggal=current_date,
                        list_jadwal_obj=template,
                        kuota=kuota_otomatis
                    )
                    
                    if new_jadwal:
                        count_created += 1
                    else:
                        print(f"  [ERROR] Gagal create DB: {error_msg}")

            db.session.commit()
            print(f"=== [FINISH] Berhasil membuat {count_created} jadwal baru. ===\n")
            return count_created

        except Exception as e:
            db.session.rollback()
            print(f"=== [CRITICAL ERROR] Rollback dilakukan: {e} ===\n")
            raise e