from fastapi import APIRouter, HTTPException, Depends
from config.token import verify_token, create_jwt_token 
from database.change_password import get_employee_id_by_email, perform_password_reset, update_user_password
from auth.credentials import generate_temp_password
from auth.hashing import get_hash_password, verify_password
from database.auth import get_user_id_and_role, get_username_by_id, get_username_by_emp_id, get_password_hash_by_user_id
from database.auth import get_user_auth_state_by_id
from config.email_sender import send_email
from logs.logger import action_logger
from schemas.password import ChangePasswordRequest, PasswordResetRequest, PasswordUpdateAfterResetRequest

password_router = APIRouter()

@password_router.post("/change-password/")
async def change_password(request: ChangePasswordRequest, token_data: dict = Depends(verify_token)):
    user_id = token_data["user_id"]
    username = get_username_by_id(user_id)
    password_hash = get_password_hash_by_user_id(user_id)
    if verify_password(request.new_password, password_hash):
        raise HTTPException(status_code=400, detail="Новий пароль не може бути таким же, як старий")
    if not username:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    if not request.new_password:
        raise HTTPException(status_code=400, detail="Пароль не може бути пустим")

    # Оновлення пароля в базі даних
    new_password_hash = get_hash_password(request.new_password)
    result = update_user_password(username, new_password_hash)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])  
    action_logger.info(f"[CHANGE PASSWORD] Користувач '{username}' змінив свій пароль")
    return {"message": "Пароль успішно змінено"}

@password_router.post("/change-password-after-reset/")
async def change_password(request: PasswordUpdateAfterResetRequest):
    """Обробник запиту на зміну пароля після скидання"""
    
    # Перевірка вхідних даних
    if not request.new_password:
        raise HTTPException(status_code=400, detail="Пароль не може бути пустим")
    if not request.user_id:
        raise HTTPException(status_code=400, detail="Відсутні дані користувача")
    state=get_user_auth_state_by_id(request.user_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    if state==0:
        raise HTTPException(status_code=403, detail="Пароль не є тимчасовим, зміна пароля після скидання не потрібна")
    username= get_username_by_id(request.user_id)
    # Викликаємо функцію оновлення пароля
    new_password_hash = get_hash_password(request.new_password)
    result = update_user_password(username, new_password_hash)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    user_data=get_user_id_and_role(username)
    if not user_data:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    token = create_jwt_token(user_data["user_id"], user_data["role"])
    if not token:
        raise HTTPException(status_code=500, detail="Не вдалося створити токен")
    action_logger.info(f"[CHANGE PASSWORD AFTER RESET] Користувач '{username}' змінив свій пароль після скидання")
    return {"message": result["message"], "token": token}

@password_router.post("/reset-password/")  
async def reset_password(request: PasswordResetRequest):
    employee_id = get_employee_id_by_email(request.email)
    if employee_id is None:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    username = get_username_by_emp_id(employee_id)
    if not username:
        raise HTTPException(status_code=404, detail="Працівника не знайдено")
    new_password = generate_temp_password()
    hashed_password = get_hash_password(new_password)
    result = perform_password_reset(username, hashed_password)
    if not result:
        raise HTTPException(status_code=500, detail="Не вдалося скинути пароль. Користувача не знайдено.")
    send_email(
        to=request.email,
        subject="Відновлення доступу до облікового запису",
        body=f"""
    Доброго дня!

    На ваш запит був згенерований тимчасовий пароль для доступу до облікового запису:

    Тимчасовий пароль: {new_password}

    Ви можете увійти до системи, використовуючи цей пароль. Після входу вам буде запропоновано змінити його — будь ласка, зробіть це одразу з міркувань безпеки.

    Якщо ви не ініціювали процедуру відновлення доступу, рекомендуємо якнайшвидше звернутися до адміністратора системи.

    З повагою,  
    Служба підтримки системи обліку WMS
    """
    )
    action_logger.info(f"[RESET PASSWORD] Користувач '{username}' отримав тимчасовий пароль для доступу до облікового запису")
    return {
        "message": "Тимчасовий пароль надіслано на вашу електронну пошту. Перевірте скриньку та увійдіть із надісланим паролем."
    }



