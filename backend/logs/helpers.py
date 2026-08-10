import os
import zipfile
from pathlib import Path
from datetime import datetime, date, timedelta

# Базові шляхи
BASE_LOG_DIR = Path("logs")
ACTIVE_DIR = BASE_LOG_DIR / "active"
ARCHIVE_DIR = BASE_LOG_DIR / "archives"

# Імена логів (мають збігатися з тими, що в setup_time_rotating_logger)
LOG_FILES = {
    "login": "login_attempts.log",
    "actions": "user_actions.log",
}

def get_date_range(date_from: str, date_to: str):
    """Генерує список дат між двома точками включно"""
    start = datetime.strptime(date_from, "%Y-%m-%d").date()
    end = datetime.strptime(date_to, "%Y-%m-%d").date()
    delta = end - start
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]

def archive_log_file(log_type: str, date_from: str = None, date_to: str = None, all_dates: bool = False) -> Path:
    if log_type not in LOG_FILES:
        raise ValueError("Невідомий тип логів")

    main_log_name = LOG_FILES[log_type]
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    archive_path = ARCHIVE_DIR / f"backup_{main_log_name}_{timestamp}.zip"

    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        files_to_add = []
        
        if all_dates:
            files_to_add = list(ACTIVE_DIR.glob(f"{main_log_name}*"))
        elif date_from and date_to:
            dates = get_date_range(date_from, date_to)
            today_str = date.today().strftime("%Y-%m-%d")
            
            for d in dates:
                if d == today_str:
                    files_to_add.append(ACTIVE_DIR / main_log_name)
                else:
                    # Формат TimedRotatingFileHandler: filename.YYYY-MM-DD
                    files_to_add.append(ACTIVE_DIR / f"{main_log_name}.{d}")
        else:
            files_to_add = [ACTIVE_DIR / main_log_name]

        for file in files_to_add:
            if file.exists() and file.is_file():
                zipf.write(file, arcname=file.name)

    return archive_path

def clear_log_file(log_type: str) -> None:
    """Очищує вміст активного файлу логів"""
    main_log_path = ACTIVE_DIR / LOG_FILES[log_type]
    if main_log_path.exists():
        with open(main_log_path, "w", encoding="utf-8"):
            pass

def delete_logs_by_date(log_type: str, date_from: str, date_to: str) -> None:
    """Видаляє ротаційні файли за період та очищує активний, якщо він у періоді"""
    main_log_name = LOG_FILES[log_type]
    dates = get_date_range(date_from, date_to)
    today_str = date.today().strftime("%Y-%m-%d")

    for d in dates:
        if d == today_str:
            clear_log_file(log_type)
        else:
            file_path = ACTIVE_DIR / f"{main_log_name}.{d}"
            if file_path.exists():
                os.remove(file_path)

def delete_all_logs(log_type: str) -> None:
    """Повне очищення всіх файлів певного типу"""
    clear_log_file(log_type)
    main_log_name = LOG_FILES[log_type]
    for file in ACTIVE_DIR.glob(f"{main_log_name}.*"):
        try:
            os.remove(file)
        except Exception as e:
            print(f"[WARN] Не вдалося видалити {file}: {e}")

def read_log_file(log_type: str, lines: int = 200, log_date: str = None) -> str:
    """Читає логи з урахуванням дати зміни файлу"""
    if log_type not in LOG_FILES:
        raise ValueError("Невідомий тип логів")

    filename = LOG_FILES[log_type]
    today = date.today()

    if log_date:
        try:
            log_date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Невірний формат дати")

        if log_date_obj > today:
            raise ValueError("Дата не може бути в майбутньому")

        # Перевірка: чи є файл за цю дату
        target_file = ACTIVE_DIR / (filename if log_date_obj == today else f"{filename}.{log_date}")
        
        # Виправлення проблеми "старого логу як сьогоднішнього":
        # Перевіряємо реальну дату останньої зміни файлу
        if target_file.exists():
            file_mtime = datetime.fromtimestamp(target_file.stat().st_mtime).date()
            if log_date_obj == today and file_mtime < today:
                return f"--- Записів за сьогодні ({today}) ще немає. Останні дії були {file_mtime} ---"
        else:
            raise FileNotFoundError(f"Логи за {log_date} відсутні")
    else:
        target_file = ACTIVE_DIR / filename

    if not target_file.exists():
        return "Файл логів порожній або не знайдений."

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except Exception as e:
        return f"Помилка зчитування: {str(e)}"