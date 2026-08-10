from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

# Генерація хешу пароля
def get_hash_password(password: str) -> str:
    return ph.hash(password)

# Перевірка пароля
def verify_password(input_password: str, stored_hash: str) -> bool:
    try:
        ph.verify(stored_hash, input_password)
        return True
    except VerifyMismatchError:
        return False
    except Exception as e:
        print(f"[ARGON ERROR] Помилка перевірки пароля: {e}")
        return False