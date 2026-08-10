import os
from dotenv import load_dotenv

# Завантажуємо змінні з файлу .env у оточення
load_dotenv()

# JWT налаштування
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

# Параметри бази даних
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "WarehouseDB")

DB_AUTH_PASSWORD = os.getenv("DB_AUTH_PASSWORD", "default_auth_password")
DB_CHANGE_PASSWORD = os.getenv("DB_CHANGE_PASSWORD", "default_change_password")
DB_ADMIN_PASSWORD = os.getenv("DB_ADMIN_PASSWORD", "default_admin_password")

MYSQL_PATH_VARIABLE = os.getenv("MYSQL_PATH", "mysql")

# Конфігурації підключень
DB_CONFIG_AUTH = {
    "host": DB_HOST,
    "user": "auth_reader",
    "password": DB_AUTH_PASSWORD,
    "database": DB_NAME,
}

DB_CONFIG_CHANGE_PASSWORD = {
    "host": DB_HOST,
    "user": "password_reset_user",
    "password": DB_CHANGE_PASSWORD,
    "database": DB_NAME,
}

DB_CONFIG_ADMIN = {
    "host": DB_HOST,
    "user": "warehouse_admin_db",
    "password": DB_ADMIN_PASSWORD,
    "database": DB_NAME,
}

# Додаткові налаштування
TEMP_PASSWORD_LENGTH = int(os.getenv("TEMP_PASSWORD_LENGTH", 10))
BACKUP_SECRET_KEY = os.getenv("BACKUP_SECRET_KEY", "default_backup_key")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", 7))
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 30))

print(f"Loaded configuration: JWT_SECRET_KEY={JWT_SECRET_KEY}, JWT_ALGORITHM={JWT_ALGORITHM}, JWT_EXPIRATION_HOURS={JWT_EXPIRATION_HOURS}, DB_HOST={DB_HOST}, DB_NAME={DB_NAME}, TEMP_PASSWORD_LENGTH={TEMP_PASSWORD_LENGTH}, BACKUP_SECRET_KEY={BACKUP_SECRET_KEY}")
print(f"Database Configurations: DB_CONFIG_AUTH={DB_CONFIG_AUTH}, DB_CONFIG_CHANGE_PASSWORD={DB_CONFIG_CHANGE_PASSWORD}, DB_CONFIG_ADMIN={DB_CONFIG_ADMIN}")
print(f"MySQL Path: {MYSQL_PATH_VARIABLE}")