import pymysql
from database.utils.connection_manager import get_db_connection
from fastapi import HTTPException

category_to_section = {
    "Автотовари": "Секція: Автотовари",
    "Книги": "Секція: Книги",
    "Побутова хімія": "Секція: Побутова хімія",
    "Одяг": "Секція: Одяг",
    "Електроніка": "Секція: Електроніка",
    "Їжа": "Секція: Їжа",
    "Меблі": "Секція: Меблі",
    "Сад та інструменти": "Секція: Сад та інструменти",
    "Здоров’я та краса": "Секція: Здоров’я та краса",
    "Побутова техніка": "Секція: Побутова техніка",
    "Канцелярія": "Секція: Канцелярія",
    "Зоотовари": "Секція: Зоотовари",
    "Спорт та туризм": "Секція: Спорт та туризм",
    "Технології": "Секція: Технології",
    "Іграшки та ігри": "Секція: Іграшки та ігри"
}

def get_products_full_function(config, search=None, expire_date=False, has_expired = False, section=None, name_filter=None, category_filter=None, price_min=None, price_max=None, sort_order='price_asc'):
    base_query = """
        SELECT 
            p.product_id, 
            p.name, 
            p.description, 
            p.price, 
            p.quantity, 
            p.expiration_date, 
            p.unit,
            c.name AS category_name, 
            s.name AS supplier_name,
            ws.name as section_name
        FROM Products p
        LEFT JOIN ProductCategories c ON p.category_id = c.category_id
        LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN WarehouseSections ws ON p.section_id = ws.section_id
    """

    where_clauses = []
    params = []

    if search:
        where_clauses.append("(p.name LIKE %s OR p.description LIKE %s OR c.name LIKE %s OR s.name LIKE %s)")
        like_value = f"%{search}%"
        params.extend([like_value, like_value, like_value, like_value])

    if expire_date:
        where_clauses.append("p.expiration_date IS NOT NULL") #AND p.expiration_date < NOW()")

    if has_expired:
        where_clauses.append("p.expiration_date < NOW()")

    if section:
        where_clauses.append("ws.name = %s")  
        params.append(section)

    if name_filter:
        where_clauses.append("p.name LIKE %s")
        like_value = f"%{name_filter}%"
        params.append(like_value)

    if category_filter:
        placeholders = ','.join(['%s'] * len(category_filter))
        where_clauses.append(f"c.name IN ({placeholders})")
        params.extend(category_filter)

    if price_min is not None:
        where_clauses.append("p.price >= %s")
        params.append(price_min)

    if price_max is not None:
        where_clauses.append("p.price <= %s")
        params.append(price_max)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # Додамо сортування за різними параметрами
    if sort_order == "price_asc":
        order_by = "p.price ASC"
    elif sort_order == "price_desc":
        order_by = "p.price DESC"
    elif sort_order == "quantity_asc":
        order_by = "p.quantity ASC"
    elif sort_order == "quantity_desc":
        order_by = "p.quantity DESC"
    elif sort_order == "name_asc":
        order_by = "p.name ASC"
    elif sort_order == "name_desc":
        order_by = "p.name DESC"
    elif sort_order == "expiration_date_asc":
        order_by = "p.expiration_date ASC"
    elif sort_order == "expiration_date_desc":
        order_by = "p.expiration_date DESC"
    else:
        order_by = "p.price ASC"  # За замовчуванням сортуємо за ціною по зростанню

    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(base_query, params)
        return cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_products_function(config, page, limit, search=None, expire_date=False, has_expired = False, section=None, name_filter=None, category_filter=None, price_min=None, price_max=None, sort_order='price_asc'):
    offset = (page - 1) * limit
    print(f"Fetching products with filters: search='{search}', expire_date={expire_date}, has_expired={has_expired}, section='{section}', name_filter='{name_filter}', category_filter={category_filter}, price_min={price_min}, price_max={price_max}, sort_order='{sort_order}', page={page}, limit={limit}")
    base_query = """
        SELECT 
            p.product_id, 
            p.name, 
            p.description, 
            p.price, 
            p.quantity, 
            p.expiration_date, 
            p.unit,
            c.name AS category_name, 
            s.name AS supplier_name,
            ws.name as section_name
        FROM Products p
        LEFT JOIN ProductCategories c ON p.category_id = c.category_id
        LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN WarehouseSections ws ON p.section_id = ws.section_id
    """

    where_clauses = []
    params = []

    if search:
        where_clauses.append("(p.name LIKE %s OR p.description LIKE %s OR c.name LIKE %s OR s.name LIKE %s)")
        like_value = f"%{search}%"
        params.extend([like_value, like_value, like_value, like_value])

    if expire_date:
        where_clauses.append("p.expiration_date IS NOT NULL") #AND p.expiration_date < NOW()")

    if has_expired:
        where_clauses.append("p.expiration_date < NOW()")

    if section:
        where_clauses.append("ws.name = %s")  
        params.append(section)

    if name_filter:
        where_clauses.append("p.name LIKE %s")
        like_value = f"%{name_filter}%"
        params.append(like_value)

    if category_filter:
        placeholders = ','.join(['%s'] * len(category_filter))
        where_clauses.append(f"c.name IN ({placeholders})")
        params.extend(category_filter)

    if price_min is not None:
        where_clauses.append("p.price >= %s")
        params.append(price_min)

    if price_max is not None:
        where_clauses.append("p.price <= %s")
        params.append(price_max)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # Додамо сортування за різними параметрами
    if sort_order == "price_asc":
        order_by = "p.price ASC"
    elif sort_order == "price_desc":
        order_by = "p.price DESC"
    elif sort_order == "quantity_asc":
        order_by = "p.quantity ASC"
    elif sort_order == "quantity_desc":
        order_by = "p.quantity DESC"
    elif sort_order == "name_asc":
        order_by = "p.name ASC"
    elif sort_order == "name_desc":
        order_by = "p.name DESC"
    elif sort_order == "expiration_date_asc":
        order_by = "p.expiration_date ASC"
    elif sort_order == "expiration_date_desc":
        order_by = "p.expiration_date DESC"
    else:
        order_by = "p.price ASC"  # За замовчуванням сортуємо за ціною по зростанню

    base_query += f"""
        ORDER BY {order_by}
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        print("Parameters for query:", params)
        print("Executing query:", base_query)
        cursor.execute(base_query, params)
        return cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def count_total_products(config, search=None, expire_date=False, has_expired = False, section=None,name_filter=None, category_filter=None, price_min=None, price_max=None):
    query = """
        SELECT COUNT(DISTINCT p.product_id) AS total
        FROM Products p
        LEFT JOIN ProductCategories c ON p.category_id = c.category_id
        LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN WarehouseSections ws ON p.section_id = ws.section_id
    """
    conditions = []
    params = []

    if search:
        conditions.append("(p.name LIKE %s OR p.description LIKE %s OR c.name LIKE %s OR s.name LIKE %s)")
        like_value = f"%{search}%"
        params.extend([like_value, like_value, like_value, like_value])

    if expire_date:
        conditions.append("p.expiration_date IS NOT NULL")
        # conditions.append("p.expiration_date < NOW()")
    
    if has_expired:
        conditions.append("p.expiration_date < NOW()")

    if section:
        conditions.append("ws.name = %s") 
        params.append(section)

    if name_filter:
        conditions.append("p.name LIKE %s")
        like_value = f"%{name_filter}%"
        params.append(like_value)

    if category_filter:
        placeholders = ','.join(['%s'] * len(category_filter))
        conditions.append(f"c.name IN ({placeholders})")
        params.extend(category_filter)

    if price_min is not None:
        conditions.append("p.price >= %s")
        params.append(price_min)

    if price_max is not None:
        conditions.append("p.price <= %s")
        params.append(price_max)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        connection.close()


def delete_product_from_db(config, product_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Перевірка: чи є не shipped замовлення з цим продуктом
        check_query = """
            SELECT o.order_id
            FROM Orders o
            JOIN OrderDetails od ON o.order_id = od.order_id
            WHERE od.product_id = %s AND o.status != 'shipped'
        """
        cursor.execute(check_query, (product_id,))
        results = cursor.fetchall()

        if results:
            raise HTTPException(
                status_code=400,
                detail="Товар не може бути видалений, оскільки використовується в активних замовленнях."
            )

        # Якщо все ок — видаляємо
        delete_query = "DELETE FROM Products WHERE product_id = %s"
        cursor.execute(delete_query, (product_id,))
        connection.commit()
        return cursor.rowcount > 0

    except pymysql.MySQLError as err:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        cursor.close()
        connection.close()


def update_product_function(config, product_id, name, category, price, description, unit, expiration_date, supplier_name):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    warning_message = None

    try:
        # Отримуємо ID категорії
        cursor.execute("SELECT category_id FROM ProductCategories WHERE name = %s", (category,))
        category_id = cursor.fetchone()
        if category_id:
            category_id = category_id[0]
        else:
            raise ValueError("Категорія не знайдена")

        # Отримуємо ID постачальника
        cursor.execute("SELECT supplier_id FROM Suppliers WHERE name = %s", (supplier_name,))
        supplier_id = cursor.fetchone()
        if supplier_id:
            supplier_id = supplier_id[0]
        else:
            raise ValueError("Постачальник не знайдений")

        # Отримуємо останню закупівельну ціну
        cursor.execute("""
            SELECT purchase_price 
            FROM StockMovements 
            WHERE product_id = %s AND movement_type = 'in'
            ORDER BY movement_date DESC 
            LIMIT 1
        """, (product_id,))
        result = cursor.fetchone()
        if result:
            last_purchase_price = result[0]
            if price <= last_purchase_price:
                warning_message = (
                    f"Зверніть увагу: вказана ціна ({price}) "
                    f"нижча або дорівнює останній закупівельній ціні ({last_purchase_price})."
                )

        # Оновлюємо продукт
        update_query = """
            UPDATE Products 
            SET name = %s, category_id = %s, price = %s,
                description = %s, unit = %s, expiration_date = %s, supplier_id = %s
            WHERE product_id = %s
        """
        cursor.execute(update_query, (
            name, category_id, price, description, unit, expiration_date, supplier_id, product_id
        ))
        connection.commit()

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return {"success": False, "error": str(err)}
    finally:
        cursor.close()
        connection.close()

    response = {"success": True, "message": "Інформацію про продукт успішно оновлено."}
    if warning_message:
        response["warning"] = warning_message
    return response

def add_product_to_db(config, name, category, price, description, unit, expiration_date, supplier_name):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Отримуємо ID категорії
        cursor.execute("SELECT category_id FROM ProductCategories WHERE name = %s", (category,))
        category_id = cursor.fetchone()
        if category_id:
            category_id = category_id[0]
        else:
            raise ValueError("Категорія не знайдена")

        # Отримуємо ID постачальника
        cursor.execute("SELECT supplier_id FROM Suppliers WHERE name = %s", (supplier_name,))
        supplier_id = cursor.fetchone()
        if supplier_id:
            supplier_id = supplier_id[0]
        else:
            raise ValueError("Постачальник не знайдений")
        
        section_name = category_to_section.get(category)
        if not section_name:
            raise ValueError("Секція для категорії не знайдена")

        cursor.execute("SELECT section_id FROM WarehouseSections WHERE name = %s", (section_name,))
        section_id = cursor.fetchone()
        if section_id:
            section_id = section_id[0]
        else:
            raise ValueError("Секція не знайдена у базі даних")


        # Додаємо продукт
        insert_query = """
            INSERT INTO Products (name, category_id, price, quantity, description, unit, expiration_date, supplier_id, section_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        cursor.execute(insert_query, (name, category_id, price, 0, description, unit, expiration_date, supplier_id,section_id))
        connection.commit()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

    return True

def get_categories_function(config):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT name FROM ProductCategories")
        categories = cursor.fetchall()
        return [category["name"] for category in categories]
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def fetch_products_from_db(config, mode="all"):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        base_query = """
            SELECT 
                p.product_id,
                p.name,
                p.price,
                p.unit,
                p.quantity AS available_quantity,
                ws.name AS section_name,
                ws.section_id,
                s.name AS supplier_name
            FROM Products p
            LEFT JOIN WarehouseSections ws ON p.section_id = ws.section_id
            LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
        """

        if mode == "available":
            base_query += " WHERE p.quantity > 0"
        elif mode == "all":
            base_query += " WHERE p.supplier_id IS NOT NULL AND p.supplier_id != 0"
        else:
            raise ValueError(f"Невідомий режим вибірки: {mode}")

        cursor.execute(base_query)
        return cursor.fetchall()

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        raise Exception(f"Помилка БД: {err}")

    finally:
        cursor.close()
        connection.close()

def get_product_by_id(config, product_id):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute( """
        SELECT product_id, name
        FROM Products
        WHERE product_id = %s
        """, (product_id,))
        result = cursor.fetchone()
        if result:
            return {"product_id": result['product_id'], "name": result['name']}
        return None

    except pymysql.MySQLError as err:
        raise Exception(f"Помилка БД: {err}")

    finally:
        cursor.close()
        connection.close()