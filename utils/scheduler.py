from datetime import datetime, timedelta, date
from extensions import mail, Message
from models import Reservasi, db
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
                    
                    dokter_nama = res.jadwalpemeriksaan.dokter.nama_dokter
                    poli_nama = res.jadwalpemeriksaan.poliklinik.nama_poli
                    jadwal_reservasi = res.tanggal_reservasi

                    try:
                        jam_mulai_dokter = res.jadwalpemeriksaan.jam_mulai
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