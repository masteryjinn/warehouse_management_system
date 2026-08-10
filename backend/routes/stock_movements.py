from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List
import dependencies as deps
import database.stock_movements as db_stock_movements
from logs.logger import action_logger
from schemas.stock_movements import IncomingItem, RelocationRequest, WriteOffRequest, StockMovementFilterParams

stock_movements_router = APIRouter(prefix="/stock_movements", tags=["Stock Movements"])

@stock_movements_router.post("/relocate")
async def relocate_stock(
    data: RelocationRequest,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    section_id = data.section_id
    items = data.items

    if not section_id or not items:
        raise HTTPException(status_code=400, detail="Неповні дані для переміщення")

    try:
        db_stock_movements.relocate_items(USER_CONFIG, section_id, items)
        action_logger.info(
            f"[RELOCATION] Користувач '{USER_CONFIG['user']}' перемістив {len(items)} товар(ів) до секції ID={section_id}"
        )
        for item in items:
            action_logger.debug(
                f"[RELOCATION ITEM] → продукт ID={item.product_id}, кількість={item.quantity}"
            )
        return {"message": "Переміщення виконано успішно"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        action_logger.error(f"[RELOCATION ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")

@stock_movements_router.post("/add_incoming")
async def add_income(
    items: List[IncomingItem],
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):          
    try:
        db_stock_movements.add_income_items_to_db(USER_CONFIG, items)
        action_logger.info(
            f"[INCOME] Користувач '{USER_CONFIG['user']}' додав надходження з {len(items)} позицій"
        )
        for item in items:
            action_logger.debug(
                f"[INCOME ITEM] → продукт ID={item.product_id}, кількість={item.quantity}, секція={item.section}, ціна={item.purchase_price}"
            )
        return {"message": "Надходження успішно додано"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("[SERVER ERROR]:", e)
        action_logger.error(f"[INCOME ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    
@stock_movements_router.get("/")
async def get_stock_movements_endpoint(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    filters: StockMovementFilterParams = Depends() 
):
    filter_data = filters.model_dump(exclude_none=True)
    total_items = db_stock_movements.count_stock_movements(USER_CONFIG, **filter_data)
    total_pages = max((total_items + limit - 1) // limit, 1)

    if page > total_pages:
        raise HTTPException(status_code=400, detail="Сторінка виходить за межі")

    items = db_stock_movements.get_stock_movements(USER_CONFIG, page, limit, **filter_data)
    return {
        "items": items,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page
    }

@stock_movements_router.post("/write_off")
async def write_off_items(
    request: WriteOffRequest, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    try:
        db_stock_movements.write_off_items_to_db(USER_CONFIG, request.items)

        # Логування дії
        action_logger.info(
            f"[WRITE_OFF] Користувач '{USER_CONFIG['user']}' списав {len(request.items)} товарів"
        )
        for item in request.items:
            action_logger.debug(
                f"[WRITE_OFF ITEM] → продукт ID={item.product_id}, кількість={item.quantity}, секція={item.section_id}, причина={item.reason}"
            )

        return {"message": "Товари успішно списані"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        action_logger.error(f"[WRITE_OFF ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера при списанні")
