import pymysql
from pymysql.cursors import DictCursor
from fastapi import HTTPException
from database.utils.connection_manager import get_db_connection

def get_all_sections(config):
    base_query = "SELECT section_id, name, location FROM WarehouseSections WHERE section_type = 'storage'"
    
    connection = get_db_connection(config)
    cursor = connection.cursor(DictCursor)
    
    try:
        cursor.execute(base_query)
        sections = cursor.fetchall()  # Отримуємо всі записи
        return sections
    except pymysql.MySQLError as err:
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        cursor.close()
        connection.close()

def count_total_sections(config, search=None, is_empty=False):
    query = """
        SELECT COUNT(DISTINCT s.section_id) AS total
        FROM WarehouseSections s
        LEFT JOIN Products p ON s.section_id = p.section_id
        LEFT JOIN Employees e ON s.employee_id = e.employee_id
    """
    conditions = []
    params = []

    if search:
        conditions.append("(s.name LIKE %s OR s.location LIKE %s OR e.name LIKE %s)")
        like_value = f"%{search}%"
        params.extend([like_value, like_value, like_value])

    if is_empty:
        # Перевіряємо, чи немає жодного продукту в секції
        conditions.append("NOT EXISTS (SELECT 1 FROM Products p2 WHERE p2.section_id = s.section_id)")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        print(f"[count_total_sections] Executing: {query} | params: {params}")
        cursor.execute(query, params)
        result = cursor.fetchone()
        print(f"[count_total_sections] Result: {result}")
        return result[0] if result else 0
    except pymysql.MySQLError as err:
        print(f"[count_total_sections] DB ERROR: {err}")
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        cursor.close()
        connection.close()

def get_sections_function(config, page, limit, search=None, is_empty=False):
    offset = (page - 1) * limit

    base_query = """
        SELECT 
            s.section_id,
            s.name,
            s.location,
            s.section_type,  
            MAX(CASE WHEN p.product_id IS NOT NULL THEN 1 ELSE 0 END) AS has_products,
            e.name AS employee_name,
            ce.contact_value AS employee_phone
        FROM WarehouseSections s
        LEFT JOIN Products p ON s.section_id = p.section_id
        LEFT JOIN Employees e ON s.employee_id = e.employee_id
        LEFT JOIN Contacts_employees ce ON e.employee_id = ce.employee_id AND ce.contact_type = 'phone' 
    """

    where_clauses = []
    params = []

    if search:
        # Додаємо пошук по назві секції та локації
        where_clauses.append("(s.name LIKE %s OR s.location LIKE %s OR e.name LIKE %s)")
        like_value = f"%{search}%"
        params.extend([like_value, like_value, like_value])

    if is_empty:
        where_clauses.append("""
            s.section_type = 'storage' AND 
            NOT EXISTS (
                SELECT 1 FROM Products p2 WHERE p2.section_id = s.section_id
            )
        """)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += """
        GROUP BY s.section_id, s.location, e.employee_id, ce.contact_value
        ORDER BY s.section_id
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        print(f"[get_sections_function] Executing: {base_query} | params: {params}")
        cursor.execute(base_query, params)
        result = cursor.fetchall()
        print(f"[get_sections_function] Result count: {len(result)}")
        return result
    except pymysql.MySQLError as err:
        print(f"[get_sections_function] DB ERROR: {err}")
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        cursor.close()
        connection.close()

def add_section_to_db(config, name, location, employee_name):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Отримуємо ID працівника за ім'ям
        cursor.execute("SELECT employee_id FROM Employees WHERE name = %s", (employee_name,))
        result = cursor.fetchone()
        if not result:
            print(f"Працівника з ім'ям '{employee_name}' не знайдено.")
            return None

        employee_id = result[0]

        # Додаємо секцію до таблиці WarehouseSections з типом 'storage'
        cursor.execute("""
            INSERT INTO WarehouseSections (name, location, employee_id, section_type)
            VALUES (%s, %s, %s, 'storage')
        """, (name, location, employee_id))

        connection.commit()
        return cursor.lastrowid  # Повертаємо ID нової секції

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")

    finally:
        cursor.close()
        connection.close()


def update_section_function(config, section_id, name, location, employee_name):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Отримуємо ID працівника за ім’ям
        cursor.execute("SELECT employee_id FROM Employees WHERE name = %s", (employee_name,))
        result = cursor.fetchone()
        if not result:
            print(f"Працівника з ім’ям '{employee_name}' не знайдено.")
            return False

        employee_id = result[0]

        # Оновлюємо дані секції
        cursor.execute("""
            UPDATE WarehouseSections
            SET name = %s, location = %s, employee_id = %s
            WHERE section_id = %s
        """, (name, location, employee_id, section_id))

        connection.commit()
        return True

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")

    finally:
        cursor.close()
        connection.close()

def delete_section_from_db(config, section_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Перевіряємо, чи секція є пакувальною
        cursor.execute("""
            SELECT section_type FROM WarehouseSections
            WHERE section_id = %s
        """, (section_id,))
        section_type = cursor.fetchone()

        if section_type is None:
            raise HTTPException(status_code=404, detail="Секція не знайдена.")
        
        # Якщо це пакувальна секція, не дозволяємо видалити
        if section_type[0] == 'packaging':
            raise HTTPException(status_code=400, detail="Неможливо видалити пакувальну секцію.")

        # Перевіряємо, чи до секції прив’язані продукти
        cursor.execute("""
            SELECT COUNT(*) FROM Products
            WHERE section_id = %s
        """, (section_id,))
        product_count = cursor.fetchone()[0]

        if product_count > 0:
            raise HTTPException(status_code=400, detail="Неможливо видалити секцію: до неї прив’язані продукти.")

        # Видаляємо секцію
        cursor.execute("""
            DELETE FROM WarehouseSections
            WHERE section_id = %s
        """, (section_id,))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Секція не знайдена або вже була видалена.")

        return {"message": "Секцію успішно видалено."}

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")

    finally:
        cursor.close()
        connection.close()

