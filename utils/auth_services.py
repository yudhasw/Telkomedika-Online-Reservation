import re
from models import Admin, Pasien

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

    password = cleaned["password"]
    if not password:
        errors["password"] = "Password tidak boleh kosong."
    elif len(password) < 8:
        errors["password"] = "Password minimal 8 karakter."
    elif not re.search(r"[0-9]", password):
        errors["password"] = "Password harus berisi minimal 1 angka."
    
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

    confirm_password = cleaned["confirm"]
    if password != confirm_password:
        errors["confirm"] = "Konfirmasi password tidak cocok."

    if any(value is not None for value in errors.values()):
        return False, errors, cleaned
    
    return True, errors, cleaned

# import re
# from models import Admin, Pasien

# def validate_register(data):
#   errors = {
#     "nama" : None,
#     "email" : None,
#     "password" : None,
#     "phone" : None,
#     "confirm" : None,
#   }

#   cleaned = {
#     "nama": data.get("nama", ""),
#     "email": data.get("email", ""),
#     "phone" : data.get("nomor_hp", ""),
#     "tgl_lahir" : data.get("tanggal_lahir", ""),
#     "jenis_kelamin" : data.get("jenis_kelamin", ""),
#     "password": "",
#     "confirm": "",
#   }

#   nama = cleaned["nama"]
#   if not nama:
#     errors["nama"] = "Nama tidak boleh kosong."
#   elif len(nama) < 3:
#     errors["nama"] = "Nama minimal 3 karakter."

#   email = cleaned["email"]
#   if not email:
#     errors["email"] = "Email tidak boleh kosong."
#   elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
#     errors["email"] = "Format email tidak valid."

#   password = data.get("password", "")
#   if not password:
#     errors["password"] = "Password tidak boleh kosong."
#   elif len(password) < 8:
#     errors["password"] = "Password minimal 8 karakter."
#   elif not re.search(r"[0-9]", password):
#     errors["password"] = "Password harus berisi minimal 1 angka."
#   elif not re.search(r"[A-Z]", password):
#     errors["password"] = "Password harus mengandung huruf kapital."
#   elif not re.search(r"[a-z]", password):
#     errors["password"] = "Password harus mengandung huruf kecil."
#   elif not re.search(r"[!@#$%&?\":{}|<>_\-+=/\\\[\];']", password):
#     errors["password"] = "Password harus mengandung simbol."

#   phone = cleaned["phone"]
#   # if not phone:
#   #   errors["phone"] = "Nomor Hp tidak boleh kosong."
#   # phone = phone.strip()
#   # phone = phone.replace(" ", "").replace("-", "")
#   if not phone:
#     errors["phone"] = "Nomor Hp tidak boleh kosong."
#   else:
#     phone = phone.strip().replace(" ", "").replace("-", "")
#     cleaned["phone"] = phone 

#     if not re.match(r"^(08\d{8,13}|\+628\d{7,12})$", phone):
#       errors["phone"] = "Format nomor HP tidak valid. Gunakan format 08xxxx atau 628xxxx"
#     elif phone.count(phone[0]) == len(phone) or re.search(r"[A-Za-z]", phone):  
#       errors["phone"] = "Nomor HP tidak valid"

#     # if not re.match(r"^(08\d{8,13}|\+628\d{7,12})$", phone):
#     #   errors["phone"] = "Format nomor HP tidak valid. Gunakan format 08xxxx atau 628xxxx"
#     # if phone.count(phone[0]) == len(phone) or re.search(r"[A-Za-z]", phone):  
#     #     errors["phone"] = "Nomor HP tidak valid"

#   if Pasien.query.filter_by(email=email).first():
#     errors["email"] = "Email sudah digunakan."

#   confirm_password = data.get("confirm_password", "")
#   if password != confirm_password:
#     errors["confirm"] = "Konfirmasi password tidak cocok."

#   if any(errors.values()):
#     return False, errors, cleaned
  
#   return True, errors, cleaned