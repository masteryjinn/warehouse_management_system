from fastapi import APIRouter, Query, HTTPException, Depends
import dependencies as deps
from schemas.warehouse import SectionCreateUpdate
import database.warehouse as db_warehouse
from logs.logger import action_logger

warehouse_router = APIRouter(prefix="/sections", tags=["warehouse sections"])

@warehouse_router.get("/full")
async def get_sections_full(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles)
): 
    try:
        sections = db_warehouse.get_all_sections(USER_CONFIG)
        return {"data": sections}
    except Exception as e:
        print(f"[get_sections_full] ERROR: {e}")
        raise HTTPException(status_code=500, detail="Помилка сервера при отриманні секцій")

@warehouse_router.get("/")
async def get_sections_paginated(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles), 
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    is_empty: bool = Query(False),
):
    try:
        total_items = db_warehouse.count_total_sections(USER_CONFIG, search, is_empty)
        total_pages = max((total_items + limit - 1) // limit, 1)
        if page > total_pages:
            raise HTTPException(status_code=400, detail="Сторінка виходить за межі")

        sections = db_warehouse.get_sections_function(USER_CONFIG, page, limit, search, is_empty)

        return {
            "data": sections,
            "total_pages": total_pages,
            "total_items": total_items,
            "current_page": page
        }
    except Exception as e:
        print(f"[get_sections] ERROR: {e}")
        raise HTTPException(status_code=500, detail="Помилка сервера при отриманні секцій")

@warehouse_router.post("/")
async def create_section(
    data: SectionCreateUpdate, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    db_warehouse.add_section_to_db(USER_CONFIG, data.name, data.location, data.employee_name)
    action_logger.info(f"[CREATE SECTION] Користувач '{USER_CONFIG['user']}' створив секцію '{data.name}'")
    return {"message": "Секцію успішно створено"}

@warehouse_router.delete("/{section_id}")
async def remove_section(
    section_id: int, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
): 
    result = db_warehouse.delete_section_from_db(USER_CONFIG, section_id)
    if not result:
        print("[SERVER ERROR]: Не вдалося видалити секцію з бази даних")
        action_logger.error(f"[DELETE SECTION ERROR] Користувач '{USER_CONFIG['user']}' не зміг видалити секцію ID={section_id}")
        raise HTTPException(status_code=500, detail="Не вдалося видалити секцію з бази даних")
    action_logger.info(f"[DELETE SECTION] Користувач '{USER_CONFIG['user']}' видалив секцію ID={section_id}")
    return {"message": "Секцію видалено"}

@warehouse_router.put("/{section_id}")
async def update_section(
    section_id : int, 
    data: SectionCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    db_warehouse.update_section_function(USER_CONFIG, section_id, data.name, data.location, data.employee_name)
    action_logger.info(f"[UPDATE SECTION] Користувач '{USER_CONFIG['user']}' оновив дані секції ID={section_id}, ім’я='{data.name}'")
    return {"message": "Дані секції оновлено"}
