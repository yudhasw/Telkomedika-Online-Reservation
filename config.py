import urllib

SERVER_NAME = "telkomedikaserver.database.windows.net"
DATABASE_NAME = "telkomedikadb"
USERNAME = "telmedadmin"
PASSWORD = "Telmedika@##122"

params = urllib.parse.quote_plus(
    f"Driver={{ODBC Driver 18 for SQL Server}};"
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
SECRET_KEY = "2hVPX6kZ5Q"