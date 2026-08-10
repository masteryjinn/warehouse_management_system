from fastapi import APIRouter, HTTPException, Depends
from database.user_info import get_user_info_from_db 
import dependencies as deps
from logs.logger import action_logger
from schemas.user_info import UserInfo

user_router = APIRouter()

@user_router.get("/user/info", response_model=UserInfo)
async def get_user_info(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles)
):  
    try:
        user_info = get_user_info_from_db(USER_CONFIG['user'])
        if not user_info:
            raise HTTPException(status_code=404, detail="Інформація про користувача не знайдена")
        action_logger.info(f"[GET USER INFO] Користувач '{USER_CONFIG['user']}' отримав свою інформацію")
        return user_info
    except Exception as e:
        print(f"[get_user_info] ERROR: {e}")
        raise HTTPException(status_code=500, detail="Помилка сервера при отриманні інформації про користувача")
