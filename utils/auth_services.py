import re
from models import Admin, Pasien
from extensions import mail, Message


def validate_password_strength(password, confirm_password):
    if not password:
        return False, "Password tidak boleh kosong."
    
    if len(password) < 8:
        return False, "Password minimal 8 karakter."
    
    if not re.search(r"[0-9]", password):
        return False, "Password harus mengandung minimal 1 angka."
    
    if not re.search(r"[A-Z]", password):
        return False, "Password harus mengandung huruf kapital."
    
    if not re.search(r"[a-z]", password):
        return False, "Password harus mengandung huruf kecil."
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password harus mengandung minimal 1 simbol unik (!@#$%)."

    if password != confirm_password:
        return False, "Konfirmasi password tidak cocok."

    return True, None

def validate_register(data):
    errors = {
        "nama" : None,
        "email" : None,
        "password" : None,
        "phone" : None,
        "confirm" : None,
    }

    cleaned = {
        "nama": (data.get("nama") or "").strip(),
        "email": (data.get("email") or "").strip(),
        "phone" : (data.get("nomor_hp") or ""), 
        "tgl_lahir" : (data.get("tanggal_lahir") or ""),
        "jenis_kelamin" : (data.get("jenis_kelamin") or ""),
        "password": (data.get("password") or ""),
        "confirm": (data.get("confirm_password") or ""),
    }

    nama = cleaned["nama"]
    if not nama:
        errors["nama"] = "Nama tidak boleh kosong."
    elif len(nama) < 3:
        errors["nama"] = "Nama minimal 3 karakter."

    email = cleaned["email"]
    if not email:
        errors["email"] = "Email tidak boleh kosong."
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = "Format email tidak valid."
    elif Pasien.query.filter_by(email=email).first():
        errors["email"] = "Email sudah digunakan."

    is_pass_valid, pass_error = validate_password_strength(cleaned["password"], cleaned["confirm"])
    if not is_pass_valid:
        errors["password"] = pass_error
    
    phone = cleaned["phone"]
    if not phone:
        errors["phone"] = "Nomor Hp tidak boleh kosong."
    else:
        phone = phone.strip().replace(" ", "").replace("-", "")
        cleaned["phone"] = phone

        if not re.match(r"^(08\d{8,13}|\+628\d{7,12})$", phone):
            errors["phone"] = "Format nomor HP tidak valid (contoh: 0812...)"
        elif re.search(r"[A-Za-z]", phone):  
             errors["phone"] = "Nomor HP harus berupa angka"


    if any(value is not None for value in errors.values()):
        return False, errors, cleaned
    
    return True, errors, cleaned

def send_otp_email(target_email, otp_code, kategori='register'):
    try:
        subject = "Kode Verifikasi (OTP) - TelkoMedika"
 
        if kategori == 'login':
            intro = "Kami mendeteksi percobaan masuk ke akun TelkoMedika Anda."
            action_msg = "Gunakan kode berikut untuk menyelesaikan proses Login:"
        elif kategori == 'reset':
            intro = "Kami menerima permintaan untuk mereset kata sandi akun Anda."
            action_msg = "Gunakan kode berikut untuk melanjutkan proses reset password:"
        else: 
            intro = "Terima kasih telah mendaftar di TelkoMedika."
            action_msg = "Gunakan kode berikut untuk memverifikasi pendaftaran akun Anda:"

        msg = Message(
            subject=subject,
            sender="telkomedikahealth@gmail.com",
            recipients=[target_email]
        )
        msg.body = f"""
        Halo,
        
        {intro}
        {action_msg}
        
        {otp_code}
        
        Kode ini bersifat rahasia dan berlaku selama 2 menit.
        Jangan berikan kode ini kepada siapapun, termasuk pihak TelkoMedika.
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error mengirim email: {e}")
        return False