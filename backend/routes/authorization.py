from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timedelta
from collections import defaultdict

from schemas.auth import LoginRequest
from config.token import create_jwt_token, verify_token
from config.email_sender import send_email
from auth.hashing import verify_password, get_hash_password
from auth.credentials import get_user_config, generate_temp_password
from database.change_password import perform_password_reset
from database.auth import get_user
from logs.logger import login_logger

authorization_router = APIRouter()

# ========= CONFIG =========
MAX_ACCOUNT_ATTEMPTS = 5
MAX_IP_ATTEMPTS = 15

ACCOUNT_BLOCK_TIME = timedelta(hours=1)
IP_BLOCK_TIME = timedelta(minutes=30)

ADMIN_EMAIL = "irynaost95@gmail.com"

# ========= STORAGE =========
account_attempts = defaultdict(list)   # username -> timestamps
ip_attempts = defaultdict(list)        # ip -> timestamps

blocked_accounts = {}                  # username -> blocked_until
blocked_ips = {}                       # ip -> blocked_until

last_admin_alert = {}                  # ip -> datetime
last_password_reset = {}               # username -> datetime


@authorization_router.post("/login/")
async def login(request_data: LoginRequest, request: Request):
    now = datetime.now()
    ip = request.client.host
    username = request_data.username.strip()

    # ===== IP BLOCK CHECK =====
    ip_blocked_until = blocked_ips.get(ip)
    if ip_blocked_until and now < ip_blocked_until:
        minutes = int((ip_blocked_until - now).total_seconds() // 60) + 1
        raise HTTPException(
            status_code=429,
            detail=f"Система тимчасово заблокована для цього комп’ютера. Спробуйте через {minutes} хв."
        )

    # ===== ACCOUNT BLOCK CHECK =====
    acc_blocked_until = blocked_accounts.get(username)
    if acc_blocked_until and now < acc_blocked_until:
        minutes = int((acc_blocked_until - now).total_seconds() // 60) + 1
        raise HTTPException(
            status_code=429,
            detail=f"Акаунт тимчасово заблоковано. Спробуйте через {minutes} хв."
        )

    # ===== CLEAN OLD ATTEMPTS =====
    account_attempts[username] = [t for t in account_attempts[username] if now - t < ACCOUNT_BLOCK_TIME]
    ip_attempts[ip] = [t for t in ip_attempts[ip] if now - t < IP_BLOCK_TIME]

    # ===== LOAD USER =====
    user_data = get_user(username)
    if not user_data:
        login_logger.warning(f"[FAILED] User not found '{username}' IP: {ip}")
        ip_attempts[ip].append(now)
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    stored_hash, role, user_id, is_temp_password, name, email = user_data

    # ===== PASSWORD CHECK =====
    if not verify_password(request_data.password, stored_hash):

        login_logger.warning(f"[FAILED] Wrong password '{username}' IP: {ip}")

        account_attempts[username].append(now)
        ip_attempts[ip].append(now)

        # ===== IP LEVEL BLOCK =====
        if len(ip_attempts[ip]) >= MAX_IP_ATTEMPTS:
            blocked_ips[ip] = now + IP_BLOCK_TIME

            if not last_admin_alert.get(ip) or now - last_admin_alert[ip] > IP_BLOCK_TIME:
                send_email(
                    ADMIN_EMAIL,
                    "🚨 Масований перебір паролів",
                    f"З IP {ip} зафіксовано багато невдалих спроб входу. IP заблоковано на 30 хв."
                )
                last_admin_alert[ip] = now

            login_logger.warning(f"[SYSTEM BLOCK] IP {ip}")
            raise HTTPException(
                status_code=429,
                detail="Система тимчасово заблокована через підозрілу активність."
            )

        # ===== ACCOUNT LEVEL BLOCK =====
        if len(account_attempts[username]) >= MAX_ACCOUNT_ATTEMPTS:
            blocked_accounts[username] = now + ACCOUNT_BLOCK_TIME

            # Admin email
            send_email(
                ADMIN_EMAIL,
                "🚨 Атака на акаунт",
                f"Користувач '{username}' заблокований після 5 невдалих спроб. IP: {ip}"
            )

            # User reset
            if email and (not last_password_reset.get(username) or now - last_password_reset[username] > ACCOUNT_BLOCK_TIME):
                temp_password = generate_temp_password()
                perform_password_reset(username, get_hash_password(temp_password))

                send_email(
                    email,
                    "🛡️ Тимчасовий пароль",
                    f"""
Доброго дня!

Через надто багато невдалих спроб входу ваш пароль було скинуто.

Тимчасовий пароль: {temp_password}

Увійдіть і змініть його одразу.
"""
                )
                last_password_reset[username] = now

            login_logger.warning(f"[ACCOUNT BLOCK] {username}")
            raise HTTPException(
                status_code=429,
                detail="Акаунт тимчасово заблоковано. Пароль скинуто."
            )

        remaining = MAX_ACCOUNT_ATTEMPTS - len(account_attempts[username])
        raise HTTPException(
            status_code=401,
            detail=f"Невірний пароль. Залишилось спроб: {remaining}"
        )

    # ===== SUCCESS =====
    login_logger.info(f"[SUCCESS] '{username}' IP: {ip}")
    account_attempts[username].clear()

    token = None
    if is_temp_password == 0:
        token = create_jwt_token(user_id, role)

    return {
        "user_id": user_id,
        "token": token,
        "name": name,
        "role": role,
        "is_temp_password": is_temp_password
    }


@authorization_router.post("/logout/")
async def logout(token_data: dict = Depends(verify_token)):
    user_id = token_data.get("user_id")
    user = get_user_config(user_id)
    login_logger.info(f"[LOGOUT] {user['user']}")
    return {"message": "Ви успішно вийшли з системи"}
