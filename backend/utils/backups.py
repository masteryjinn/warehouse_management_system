import os
import gzip
import shutil
import datetime
import tempfile
import subprocess
from cryptography.fernet import Fernet
from config.config import DB_CONFIG_ADMIN, MYSQL_PATH_VARIABLE, BACKUP_SECRET_KEY, BACKUP_DIR, MAX_BACKUPS, BACKUP_RETENTION_DAYS

fernet = Fernet(BACKUP_SECRET_KEY.encode() if isinstance(BACKUP_SECRET_KEY, str) else BACKUP_SECRET_KEY)

def encrypt_data(data: bytes) -> bytes:
    """Шифрує байти за допомогою Fernet (AES)."""
    return fernet.encrypt(data)


def decrypt_data(data: bytes) -> bytes:
    """Дешифрує байти. Якщо дані не зашифровані — повертає як є (для сумісності)."""
    try:
        return fernet.decrypt(data)
    except Exception:
        # Якщо файл був створений раніше без шифрування
        return data


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def list_backups():
    ensure_backup_dir()
    backups = []
    now = datetime.datetime.now()
    for file in sorted(os.listdir(BACKUP_DIR), reverse=True):
        # Підтримуємо як нові зашифровані .enc, так і старі розширення
        if file.endswith((".sql.gz.enc", ".sql.gz", ".sql")):
            filepath = os.path.join(BACKUP_DIR, file)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            age_days = (now - mtime).days
            backups.append({
                "filename": file,
                "created_at": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 2),
                "age_days": age_days
            })
    return backups


def create_backup():
    ensure_backup_dir()

    # Авто-ротація за датою та кількістю (враховуємо всі бекапи)
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith((".sql.gz.enc", ".sql.gz", ".sql"))],
        key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x))
    )

    now = datetime.datetime.now()
    to_delete = []

    for f in backups:
        filepath = os.path.join(BACKUP_DIR, f)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        if (now - mtime).days > BACKUP_RETENTION_DAYS:
            to_delete.append(f)

    if len(backups) - len(to_delete) >= MAX_BACKUPS:
        num_extra = len(backups) - len(to_delete) - MAX_BACKUPS + 1
        to_delete.extend(backups[:num_extra])

    for f in set(to_delete):
        os.remove(os.path.join(BACKUP_DIR, f))
        print(f"🗑️ Видалено старий бекап: {f}")

    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Підсумковий файл з подвійним розширенням (.gz.enc)
    final_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.sql.gz.enc")
    dump_file = os.path.join(BACKUP_DIR, f"temp_{timestamp}.sql")

    try:
        # 1. Дамп БД з MySQL
        with open(dump_file, "w", encoding="utf-8") as f:
            result = subprocess.run(
                [
                    "mysqldump",
                    "-h", DB_CONFIG_ADMIN["host"],
                    "-u", DB_CONFIG_ADMIN["user"],
                    f"-p{DB_CONFIG_ADMIN['password']}",
                    DB_CONFIG_ADMIN["database"],
                ],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )
        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        # 2. Читаємо SQL, стискаємо у GZIP та ШИФРУЄМО
        with open(dump_file, "rb") as f_in:
            compressed_data = gzip.compress(f_in.read())
            encrypted_data = encrypt_data(compressed_data)

        # 3. Записуємо зашифрований файл
        with open(final_file, "wb") as f_out:
            f_out.write(encrypted_data)

        os.remove(dump_file)
        print("🔐 Зашифрований бекап успішно створено:", final_file)

        return os.path.basename(final_file)

    except Exception as e:
        if os.path.exists(dump_file):
            os.remove(dump_file)
        print("❌ ПОМИЛКА створення бекапу:", e)
        raise


def delete_backup(filename: str):
    ensure_backup_dir()
    safe_filename = os.path.basename(filename)
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith((".sql.gz.enc", ".sql.gz", ".sql"))]
    
    if safe_filename not in backups:
        raise FileNotFoundError("Файл не знайдено")
    
    if len(backups) <= 1:
        raise RuntimeError("Неможливо видалити останній бекап!")

    filepath = os.path.join(BACKUP_DIR, safe_filename)
    os.remove(filepath)
    print(f"🗑️ Видалено бекап: {safe_filename}")


def restore_from_file(file_bytes: bytes):
    """Відновлення з файлу (прийнятого по мережі або з диска сервера)."""
    try:
        # 1. ДЕШИФРУЄМО байти
        decrypted_data = decrypt_data(file_bytes)

        # 2. РОЗПАКОВУЄМО GZIP
        try:
            sql_content = gzip.decompress(decrypted_data)
        except Exception:
            sql_content = decrypted_data  # Якщо прийшов чистий SQL без архівації

        # 3. Записуємо у тимчасовий .sql файл і заливаємо в MySQL
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".sql", delete=False) as tmp_file:
            tmp_file.write(sql_content)
            tmp_file_path = tmp_file.name

        try:
            with open(tmp_file_path, "rb") as sql_input:
                subprocess.run(
                    [
                        MYSQL_PATH_VARIABLE,
                        "-h", DB_CONFIG_ADMIN["host"],
                        "-u", DB_CONFIG_ADMIN["user"],
                        f"-p{DB_CONFIG_ADMIN['password']}",
                        DB_CONFIG_ADMIN["database"],
                    ],
                    stdin=sql_input,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            print("✅ Успішно дешифровано та відновлено!")
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Помилка відновлення: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        raise RuntimeError(f"Помилка дешифрування/відновлення: {str(e)}")


def restore_backup(filename: str):
    """Відновлення за назвою файлу з серверної папки backups."""
    filepath = get_backup_file_path(filename)
    with open(filepath, "rb") as f:
        file_bytes = f.read()
    restore_from_file(file_bytes)


def get_backup_file_path(filename: str) -> str:
    ensure_backup_dir()
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(BACKUP_DIR, safe_filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError("Файл не знайдено")
    return filepath


def get_backup_file_content(filename: str) -> bytes:
    filepath = get_backup_file_path(filename)
    with open(filepath, "rb") as f:
        return f.read()