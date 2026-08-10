from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
import jwt
from datetime import datetime, timezone, timedelta
from config.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Функція для створення JWT-токена
def create_jwt_token(user_id: int, role: str):
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expiration,
        "iss": "my_server"  # Додаємо issuer для додаткової безпеки
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

# Функція для перевірки токена
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        # Декодуємо токен
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], issuer="my_server")
        return payload  # повертаємо payload, який містить user_id і role
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен прострочений")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недійсний токен")
