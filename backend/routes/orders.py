from fastapi import APIRouter, Query, HTTPException, Depends
import dependencies as deps
import database.orders as db_orders
from schemas.orders import ConfirmOrderRequest, OrderFilterParams, OrderCreate, BulkShipRequest
from utils.pdf_generator import generate_invoice_pdf
from fastapi.responses import StreamingResponse
from logs.logger import action_logger

orders_router = APIRouter(prefix="/orders", tags=["Orders"])

@orders_router.get("/")
async def get_orders(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    filters: OrderFilterParams = Depends()
):
    filter_data = filters.model_dump(exclude_none=True)
    total_items = db_orders.count_total_orders(USER_CONFIG, **filter_data)
    total_pages = max((total_items + limit - 1) // limit, 1)

    if page > total_pages:
        raise HTTPException(status_code=400, detail="Сторінка виходить за межі")

    suppliers = db_orders.get_orders_function(USER_CONFIG, page, limit, **filter_data)

    return {
        "data": suppliers,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page
    }

@orders_router.post("/")
async def create_order(
    data: OrderCreate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    order_id = db_orders.add_order_to_db(USER_CONFIG, data.customer_id)
    action_logger.info(f"[CREATE ORDER] Користувач '{USER_CONFIG['user']}' створив замовлення ID={order_id} для клієнта ID={data.customer_id}")
    return {"order_id": order_id}

@orders_router.delete("/{order_id}")
async def remove_order(
    order_id: int, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
): 
    result = db_orders.delete_orders_from_db(USER_CONFIG, order_id)
    if not result:
        raise HTTPException(status_code=500, detail="Не вдалося видалити замовлення з бази даних")
    action_logger.info(f"[DELETE ORDER] Користувач '{USER_CONFIG['user']}' видалив замовлення ID={order_id}")
    return {"message": "Замовлення видалено"}

@orders_router.put("/bulk-ship")
async def bulk_ship_orders(
    request: BulkShipRequest,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    print(f"DEBUG: Received IDs: {request.order_ids}")
    # Передаємо саме список ID з моделі
    db_orders.bulk_ship_orders_in_db(USER_CONFIG, request.order_ids)
    
    action_logger.info(f"[BULK SHIP] Користувач '{USER_CONFIG['user']}' відправив масово замовлення IDs={request.order_ids}")
    return {"message": f"Масова відправка {len(request.order_ids)} замовлень успішна"}

@orders_router.put("/{order_id}/cancel")
async def cancel_order(
    order_id: int, 
    token_data: dict = Depends(deps.verify_token),
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
): 
    user_id = token_data['user_id']
    result = db_orders.cancel_order_in_db(USER_CONFIG, order_id, user_id)
    if not result:
        raise HTTPException(status_code=500, detail="Не вдалося скасувати замовлення в базі даних. Можливо, замовлення вже відправлено або не існує.")
    action_logger.info(f"[CANCEL ORDER] Користувач '{USER_CONFIG['user']}' скасував замовлення ID={order_id}")
    return {"message": "Замовлення скасовано"}

@orders_router.put("/{order_id}")
async def confirm_order(
    order_id: int,
    data: ConfirmOrderRequest,
    token_data: dict = Depends(deps.verify_token),
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
): 
    user_id = token_data['user_id']
    db_orders.confirm_order_in_db(USER_CONFIG, order_id, data.items, user_id)
    action_logger.info(f"[CONFIRM ORDER] Користувач '{USER_CONFIG['user']}' підтвердив замовлення ID={order_id} з {len(data.items)} позиціями")
    return {"message": "Замовлення підтверджено"}

@orders_router.get("/{order_id}/details")
async def get_order_details(
    order_id: int,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles)
):
    try:
        result = db_orders.get_order_details_from_db(USER_CONFIG,order_id)

        if not result:
            return []
        action_logger.info(f"[GET ORDER DETAILS] Користувач '{USER_CONFIG['user']}' отримав деталі замовлення ID={order_id}")
        return result

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
    
@orders_router.get("/{order_id}/invoice")
async def get_order_invoice(
    order_id: int,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):

    invoice_data = db_orders.get_invoice_data_from_db(USER_CONFIG, order_id)
    if not invoice_data:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")

    pdf_buffer = generate_invoice_pdf(order_id, invoice_data)

    action_logger.info(f"[GET INVOICE] Користувач '{USER_CONFIG['user']}' отримав накладну для замовлення ID={order_id}")
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=invoice_{order_id}.pdf"}
    )
