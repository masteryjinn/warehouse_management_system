from fastapi import APIRouter, Depends, HTTPException
from database.notifications import gather_all_notifications
from config.token import verify_token 
from auth.credentials import get_user_config

notifications_router = APIRouter()

@notifications_router.get("/notifications")
async def get_notifications(token_data: dict = Depends(verify_token)):
    user_id = token_data.get("user_id")
    user_role = token_data.get("role")
    if user_role not in ("admin", "manager", "employee"):
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    config = get_user_config(user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Конфігурація користувача не знайдена")
    notifications = gather_all_notifications(config,user_role)

    return {
        "notifications": notifications,
        "count": len(notifications)
    }
