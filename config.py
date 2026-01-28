# config.py universal
SQLALCHEMY_DATABASE_URI = (
    "mssql+pyodbc://./SISTEMA_DE_RESTAURANTE_TRATTORIA?" 
    "driver=ODBC+Driver+17+for+SQL+Server&"
    "trusted_connection=yes&"
    "Encrypt=no&"
    "TrustServerCertificate=yes"
)