import random
import string
from argon2 import PasswordHasher
from config.config import TEMP_PASSWORD_LENGTH

from fastapi import HTTPException
from database.auth import get_password_hash_by_user_id, get_username_by_id


ph = PasswordHasher() 

def generate_temp_password() -> str:
    characters = string.ascii_letters + string.digits
    temp_password = ''.join(random.choice(characters) for _ in range(TEMP_PASSWORD_LENGTH))
    return temp_password

# Функція для отримання конфігурації користувача
def get_user_config(user_id: int) -> dict:
    password_hash = get_password_hash_by_user_id(user_id)

    if not password_hash:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    
    username = get_username_by_id(user_id)  

    user_config = {
        "host": "db",  # Хост бази даних
        "user": username,  # Логін до бази даних
        "password": password_hash,  # Пароль
        "database": "WarehouseDB",  # Назва бази даних
    }
    
    return user_config