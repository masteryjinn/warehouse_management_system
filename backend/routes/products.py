from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from config.token import verify_token
from datetime import datetime
import dependencies as deps
import database.products as db_products
from logs.logger import action_logger
import schemas.products as products_schemas

products_router = APIRouter(prefix="/products", tags=["Products"])

@products_router.get("/")
async def get_products(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category_filter: Optional[List[str]] = Query(None),
    filters: products_schemas.ProductFilterParams = Depends()
):
    filters_dict = filters.model_dump(exclude_none=True)
    if category_filter:
        filters_dict["category_filter"] = category_filter
    count_params = {k: v for k, v in filters_dict.items() if k != "sort_order"}
    total_items = db_products.count_total_products(USER_CONFIG, **count_params)
    total_pages = max((total_items + limit - 1) // limit, 1)

    if page > total_pages:
        raise HTTPException(status_code=400, detail="Сторінка виходить за межі")

    products = db_products.get_products_function(USER_CONFIG, page, limit, **filters_dict)
    return {
        "data": products,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page
    }

@products_router.get("/full")
async def get_products_full(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager),
    сategory_filter: Optional[List[str]] = Query(None),
    filter: products_schemas.ProductFilterParams = Depends()
):
    filters_dict = filter.model_dump(exclude_none=True)
    if сategory_filter:
        filters_dict["category_filter"] = сategory_filter
    products = db_products.get_products_full_function(USER_CONFIG, **filters_dict)
    return {"products": products}

@products_router.delete("/{product_id}")
async def remove_product(
    product_id: int,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    try:
        result = db_products.delete_product_from_db(USER_CONFIG, product_id)
        if not result:
            raise HTTPException(status_code=500, detail="Не вдалося видалити продукт з бази даних")
    except HTTPException:
        raise  # просто прокидаємо далі
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Невідома помилка: {str(e)}")
    action_logger.info(f"[DELETE PRODUCT] Користувач '{USER_CONFIG['user']}' видалив продукт ID={product_id}")
    return {"message": "Продукт успішно видалено"}

    
@products_router.put("/{product_id}")
async def update_product(
    product_id: int,
    data: products_schemas.ProductCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    try:
        res=db_products.update_product_function(
            USER_CONFIG,
            product_id,
            data.name,
            data.category,
            data.price,
            data.description,
            data.unit,
            data.expiry_date,
            data.supplier_name   
        )
        if not res:
            raise HTTPException(status_code=500, detail="Не вдалося оновити продукт")
    except HTTPException:
        raise  # просто прокидаємо далі
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Невідома помилка: {str(e)}")
    action_logger.info(
        f"[UPDATE PRODUCT] Користувач '{USER_CONFIG['user']}' оновив продукт ID={product_id}: назва='{data.name}', категорія='{data.category}', ціна={data.price}, постачальник='{data.supplier_name}'"
    )
    return {"message": "Продукт оновлено"}

@products_router.post("/")
async def add_product(
    data: products_schemas.ProductCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    res=db_products.add_product_to_db(USER_CONFIG, data.name, data.category, data.price, data.description, data.unit, data.expiry_date, data.supplier_name)
    if not res:
        raise HTTPException(status_code=500, detail="Не вдалося додати продукт")
    action_logger.info(
    f"[ADD PRODUCT] Користувач '{USER_CONFIG['user']}' додав продукт: назва='{data.name}', категорія='{data.category}', ціна={data.price}, постачальник='{data.supplier_name}'"
)
    return {"message": "Продукт додано"}

@products_router.get("/categories")
async def get_categories(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    categories = db_products.get_categories_function(USER_CONFIG)
    if not categories:
        return []
    return {"categories": categories}

@products_router.get("/all-or-available")
async def get_all_or_available_products(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager),
    available_only: Optional[bool] = Query(False, description="Повернути лише продукти з наявністю > 0")
):
    products = db_products.fetch_products_from_db(USER_CONFIG, mode="available" if available_only else "all")
    return {"products": products}

@products_router.get("/{product_id}")
def fetch_product(product_id: int, USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)):
    product = db_products.get_product_by_id(USER_CONFIG, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не знайдено")
    return product

@products_router.post("/import")
async def import_products(
    data: products_schemas.ProductsImportRequest,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    results = {"added": 0, "updated": 0, "errors": []}
    for product in data.products:
        try:
            # Перетворюємо ціну та кількість
            try:
                price = float(str(product.price).replace(",", "."))
            except (ValueError, TypeError):
                results["errors"].append({"name": product.name, "error": f"Некоректна ціна: {product.price}"})
                continue

            try:
                quantity = int(product.quantity)
            except (ValueError, TypeError):
                results["errors"].append({"name": product.name, "error": f"Некоректна кількість: {product.quantity}"})
                continue

            # Перетворюємо дату в формат MySQL YYYY-MM-DD
            expiration_date = None
            if product.expiration_date:
                try:
                    # підтримуємо формати: 27.06.2027, 2027-06-27, 27/06/2027
                    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
                        try:
                            expiration_date = datetime.strptime(product.expiration_date, fmt).date()
                            break
                        except ValueError:
                            continue
                    if not expiration_date:
                        raise ValueError
                except ValueError:
                    results["errors"].append({"name": product.name, "error": f"Некоректна дата: {product.expiration_date}"})
                    continue

            if product.product_id:
                existing = db_products.get_product_by_id(USER_CONFIG, product.product_id)
                if existing:
                    db_products.update_product_function(
                        USER_CONFIG,
                        product.product_id,
                        product.name,
                        products_schemas.category_name_to_id.get(product.category_name),
                        price,
                        quantity,
                        product.description,
                        product.unit,
                        expiration_date,
                        product.supplier_name
                    )
                    results["updated"] += 1
                    action_logger.info(f"[UPDATE PRODUCT] Користувач {USER_CONFIG['user_id']} оновив продукт ID={product.product_id}")
                else:
                    new_id = db_products.add_product_to_db(
                        USER_CONFIG,
                        product.name,
                        products_schemas.category_name_to_id.get(product.category_name),
                        price,
                        quantity,
                        product.description,
                        product.unit,
                        expiration_date,
                        product.supplier_name
                    )
                    results["added"] += 1
                    action_logger.info(f"[ADD PRODUCT] Користувач {USER_CONFIG['user_id']} додав продукт з новим ID={new_id}")
            else:
                # product_id відсутній → створюємо новий продукт
                new_id = db_products.add_product_to_db(
                    USER_CONFIG,
                    product.name,
                    products_schemas.category_name_to_id.get(product.category_name),
                    price,
                    quantity,
                    product.description,
                    product.unit,
                    expiration_date,
                    product.supplier_name
                )
                results["added"] += 1
                action_logger.info(f"[ADD PRODUCT] Користувач {USER_CONFIG['user_id']} додав продукт з новим ID={new_id}")

        except Exception as e:
            results["errors"].append({"name": product.name, "error": str(e)})

    return {"message": "Імпорт завершено", "results": results}
