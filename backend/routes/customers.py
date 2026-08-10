from fastapi import APIRouter, Query, HTTPException, Depends
import dependencies as deps
import database.customers as db_customers
from schemas.customers import CustomerCreateUpdate, CustomerImport, CustomerFilter
from logs.logger import action_logger

customers_router = APIRouter(prefix="/customers", tags=["Customers"])

@customers_router.get("/")
async def get_customers(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    filter: CustomerFilter = Depends()
):
    filter_data = filter.model_dump(exclude_none=True)
    print(filter_data)
    # Загальний підрахунок елементів
    total_items = db_customers.count_total_customers(USER_CONFIG, **filter_data)
    total_pages = max((total_items + limit - 1) // limit, 1)

    if page > total_pages:
        raise HTTPException(status_code=400, detail="Сторінка виходить за межі")

    # Отримання списку користувачів з усіма фільтрами
    customers = db_customers.get_customers_function(USER_CONFIG, page, limit, **filter_data)

    return {
        "data": customers,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page
    }

@customers_router.delete("/{customer_id}")
async def remove_customer(
    customer_id: int, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):     
    result = db_customers.delete_customer_from_db(USER_CONFIG, customer_id)
    if not result:
        raise HTTPException(status_code=500, detail="Не вдалося видалити клієнта з бази даних. Зачекайте, поки всі його замовлення будуть в статусі відправлені і повторіть спробу зновую")
    action_logger.info(f"[DELETE CUSTOMER] Користувач '{USER_CONFIG['user']}' видалив клієнта ID={customer_id}")
    return {"message": "Клієнта видалено"}

@customers_router.put("/{customer_id}")
async def update_customer(
    customer_id: int,
    data: CustomerCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    contacts = data.contacts.model_dump(exclude_none=True)
    db_customers.update_customer_function(USER_CONFIG, customer_id, data.name, data.type, contacts)
    action_logger.info(f"[UPDATE CUSTOMER] Користувач '{USER_CONFIG['user']}' оновив дані клієнта '{data.name}' (ID={customer_id})")

    return {"message": "Дані клієнта оновлено"}

@customers_router.post("/")
async def create_customer(
    data: CustomerCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    contacts = data.contacts.model_dump(exclude_none=True)
    customer_id = db_customers.add_customer_to_db(USER_CONFIG, data.name, data.type, contacts)
    action_logger.info(f"[CREATE CUSTOMER] Користувач '{USER_CONFIG['user']}' створив клієнта '{data.name}' (ID={customer_id})")

    return {"message": "Клієнта успішно створено"}

@customers_router.get("/select")
async def select_customer(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    customers=db_customers.get_customers_full(USER_CONFIG)
    if not customers:
        return []
    return {"customers": customers}

@customers_router.post("/import")
async def import_customers(
    data: CustomerImport,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    imported_count = 0
    skipped_count = 0
    imported_names = []
    skipped_names = []

    for item in data.customers:
        contacts = item.contacts.model_dump(exclude_none=True)
        result = db_customers.add_customer_to_db(USER_CONFIG, item.name, item.type, contacts)
        if result is not None:
            imported_count += 1
            imported_names.append(item.name)
        else:
            skipped_count += 1
            skipped_names.append(item.name)

    action_logger.info(
        f"[IMPORT CUSTOMERS] Користувач '{USER_CONFIG['user']}' імпортував {imported_count} нових, "
        f"пропущено {skipped_count}"
    )

    return {
        "message": f"Імпортовано {imported_count}, пропущено {skipped_count}",
        "imported_names": imported_names,
        "skipped_names": skipped_names
    }
