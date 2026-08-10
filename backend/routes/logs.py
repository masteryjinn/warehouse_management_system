from fastapi import APIRouter, Depends, HTTPException, Body, Query
from config.token import verify_token
import dependencies as deps
import logs.helpers as log_helpers
from auth.hashing import verify_password

logs_router = APIRouter()

@logs_router.delete("/logs")
async def delete_logs(
    log_type: str = Query(..., description="Тип логів: login або actions"),
    archive_before_delete: bool = Query(False, description="Архівувати перед видаленням"),
    all_dates: bool = Query(False, description="Очистити всі дати"),
    date_from: str = Query(None, description="Дата початку для видалення (формат YYYY-MM-DD)"),
    date_to: str = Query(None, description="Дата кінця для видалення (формат YYYY-MM-DD)"),
    password: str = Body(..., embed=True),
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    if not verify_password(password, USER_CONFIG["password"]):
        raise HTTPException(status_code=401, detail="Невірний пароль")

    if log_type not in log_helpers.LOG_FILES:
        raise HTTPException(status_code=400, detail="Невідомий тип логів")

    archive_path = None
    try:
        if archive_before_delete:
            archive_path = log_helpers.archive_log_file(log_type, date_from=date_from, date_to=date_to, all_dates=all_dates)

        if all_dates:
            log_helpers.delete_all_logs(log_type)
        elif date_from and date_to:
            log_helpers.delete_logs_by_date(log_type, date_from, date_to)
        else:
            log_helpers.clear_log_file(log_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка очищення логів: {str(e)}")

    return {
        "message": f"Логи '{log_type}' очищено.",
        "archived_to": str(archive_path) if archive_path else None
    }

@logs_router.get("/logs")
async def read_logs(
    log_type: str = Query(..., description="Тип логів: login або actions"),
    lines: int = Query(200, ge=10, le=1000, description="Кількість останніх рядків"),
    log_date: str = Query(None, description="Дата логу у форматі YYYY-MM-DD"),
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    try:
        log_text = log_helpers.read_log_file(log_type=log_type, lines=lines, log_date=log_date)
        return {"logs": log_text}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="За обраною датою логів не знайдено")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка читання логів: {str(e)}")