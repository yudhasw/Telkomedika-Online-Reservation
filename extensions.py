from flask_mail import Mail
from functools import wraps
from flask import redirect, url_for, flash, session
from flask_login import current_user

mail = Mail()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Silakan login untuk mengakses.', 'warning')
            return redirect(url_for('auth.login_admin'))
        
        if session.get('role') != 'admin':
            flash('Anda tidak memiliki akses admin.', 'danger')
            return redirect(url_for('auth.login_admin'))
            
        return f(*args, **kwargs)
    return decorated_function

def pasien_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login_pasien'))
            
        if session.get('role') != 'pasien':
            flash('Silakan login sebagai pasien.', 'warning')
            return redirect(url_for('auth.login_pasien'))
            
        return f(*args, **kwargs)
    return decorated_function