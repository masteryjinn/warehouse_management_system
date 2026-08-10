from fastapi import APIRouter, Query, HTTPException, Depends
import database.suppliers as db_suppliers
import dependencies as deps
from logs.logger import action_logger

from schemas.suppliers import SupplierCreateUpdate, SupplierImport, SupplierFilter

suppliers_router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@suppliers_router.get("/")
async def get_suppliers(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    filters: SupplierFilter = Depends() 
):
    filter_data = filters.model_dump(exclude_none=True)

    total_items = db_suppliers.count_total_suppliers(USER_CONFIG, **filter_data)
    total_pages = max((total_items + limit - 1) // limit, 1)

    if page > total_pages:
        raise HTTPException(status_code=400, detail="Сторінка виходить за межі")

    # Отримання списку користувачів з усіма фільтрами
    suppliers = db_suppliers.get_suppliers_function(USER_CONFIG, page, limit, **filter_data)

    return {
        "data": suppliers,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page
    }

@suppliers_router.delete("/{supplier_id}")
async def remove_suplier(
    supplier_id: int,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    if not supplier_id:
        raise HTTPException(status_code=400, detail="ID постачальника обов'язковий для заповнення")
     
    result = db_suppliers.delete_supplier_from_db(USER_CONFIG, supplier_id)
    if not result: 
        action_logger.error(f"[DELETE SUPPLIER ERROR] Користувач '{USER_CONFIG['user']}' не зміг видалити постачальника ID={supplier_id}")
        raise HTTPException(status_code=500, detail="Не вдалося видалити постачальника з бази даних")
    action_logger.info(f"[DELETE SUPPLIER] Користувач '{USER_CONFIG['user']}' видалив постачальника ID={supplier_id}")
    return {"message": "Постачальника видалено"}

@suppliers_router.put("/{supplier_id}")
async def update_suplier(
    supplier_id: int, 
    data: SupplierCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    contacts_dict = data.contacts.model_dump(exclude_none=True)
    res = db_suppliers.update_supplier_function(
        USER_CONFIG, supplier_id, data.name, data.type.value, contacts_dict
    )
    if not res:
        action_logger.error(f"[UPDATE SUPPLIER ERROR] Користувач '{USER_CONFIG['user']}' не зміг оновити дані постачальника ID={supplier_id}")
        raise HTTPException(status_code=500, detail="Не вдалося оновити дані постачальника")
    action_logger.info(f"[UPDATE SUPPLIER] Користувач '{USER_CONFIG['user']}' оновив дані постачальника ID={supplier_id}, ім’я='{data.name}'")
    return {"message": "Дані постачальника оновлено"}

@suppliers_router.post("/")
async def create_supplier(
    data: SupplierCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    contacts_dict = data.contacts.model_dump(exclude_none=True)
    db_suppliers.add_supplier_to_db(
        USER_CONFIG, data.name, data.type.value, contacts_dict
    )
    action_logger.info(f"[CREATE SUPPLIER] Користувач '{USER_CONFIG['user']}' створив постачальника '{data.name}'")
    return {"message": "Постачальника успішно створено"}

@suppliers_router.get("/select")
async def select_supplier(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles)
):
    suppliers=db_suppliers.get_suppliers_full(USER_CONFIG)
    if not suppliers:
        return []
        #raise HTTPException(status_code=404, detail="Постачальники не знайдені")
    return {"suppliers": suppliers}

@suppliers_router.post("/import")
async def import_suppliers(
    data: SupplierImport,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):              
    imported_count = 0
    skipped_count = 0
    imported_names = []
    skipped_names = []
    
    for item in data.suppliers:
        contacts = item.contacts.model_dump(exclude_none=True)

        result = db_suppliers.add_supplier_to_db(USER_CONFIG, item.name, item.type.value, contacts)
        if result is not None:
            imported_count += 1
            imported_names.append(item.name)
        else:
            skipped_count += 1
            skipped_names.append(item.name)

    action_logger.info(
        f"[IMPORT SUPPLIERS] Користувач '{USER_CONFIG['user']}' імпортував {imported_count} нових, "
        f"пропущено {skipped_count}"
    )

    return {
        "message": f"Імпортовано {imported_count}, пропущено {skipped_count}",
        "imported_names": imported_names,
        "skipped_names": skipped_names
    }
