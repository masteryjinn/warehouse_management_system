import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os
import stat

# Основна директорія
BASE_LOG_DIR = Path("logs")
ACTIVE_LOG_DIR = BASE_LOG_DIR / "active"
ARCHIVE_LOG_DIR = BASE_LOG_DIR / "archives"

# Створюємо структуру
for directory in [BASE_LOG_DIR, ACTIVE_LOG_DIR, ARCHIVE_LOG_DIR]:
    if not directory.exists():
        directory.mkdir(parents=True, mode=0o750)  # drwxr-x---

def setup_time_rotating_logger(name: str, filename: str, level=logging.INFO, when='midnight', interval=1, backup_count=7):
    log_file = ACTIVE_LOG_DIR / filename

    if not log_file.exists():
        log_file.touch()
        os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)  # 640

    handler = TimedRotatingFileHandler(
        log_file,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8",
        utc=True
    )

    # Це важливо: архіви типу login_attempts.log.2025-07-27
    handler.suffix = "%Y-%m-%d"

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger

# Приклади логерів
login_logger = setup_time_rotating_logger("login_logger", "login_attempts.log")
action_logger = setup_time_rotating_logger("action_logger", "user_actions.log")
