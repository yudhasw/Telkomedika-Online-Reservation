from threading import Thread
from flask import current_app
from extensions import mail

def send_async_email(app, msg):
  with app.app_context():
    mail.send(msg)

def send_mail(msg):
  app = current_app._get_current_object()
  Thread(target=send_async_email, args=(app, msg)).start()