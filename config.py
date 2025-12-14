import urllib
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SERVER_NAME = os.getenv("SERVER_NAME", "localhost")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "TelkomedikaDB")
    USERNAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("DB_PASSWORD")

    driver = "ODBC Driver 18 for SQL Server"

    params = urllib.parse.quote_plus(
        f"Driver={{{driver}}};"
        f"Server=tcp:{SERVER_NAME},1433;"
        f"Database={DATABASE_NAME};"
        f"Uid={USERNAME};"
        f"Pwd={PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key")

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ('TelkoMedika System', os.getenv("MAIL_USERNAME"))
