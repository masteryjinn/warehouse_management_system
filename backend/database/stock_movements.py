import pymysql
from fastapi import HTTPException
from database.utils.connection_manager import get_db_connection
from typing import List

def relocate_items(config, section_id: int, items: List):
    connection = get_db_connection(config)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Перевірка цільової секції
            cursor.execute("SELECT section_id, name FROM WarehouseSections WHERE section_id = %s", (section_id,))
            new_section = cursor.fetchone()
            if not new_section:
                raise ValueError(f"Цільову секцію з ID {section_id} не знайдено.")
            new_section_name = new_section["name"]

            for item in items:
                # Перевірка товару
                cursor.execute("SELECT * FROM Products WHERE product_id = %s", (item.product_id,))
                product = cursor.fetchone()
                if not product:
                    raise ValueError(f"Товар з ID {item.product_id} не знайдено.")

                # Отримуємо ID поточної секції
                cursor.execute("SELECT section_id FROM WarehouseSections WHERE name = %s", (item.current_section,))
                current_section = cursor.fetchone()
                if not current_section:
                    raise ValueError(f"Секція '{item.current_section}' не знайдена.")
                current_section_id = current_section["section_id"]

                # Заборона переміщення в ту ж секцію
                if current_section_id == section_id:
                    raise ValueError(f"Неможливо перемістити товар з ID {item.product_id} у ту ж секцію '{new_section_name}'.")

                if item.quantity > 0:
                    # Один запис про переміщення
                    cursor.execute("""
                        INSERT INTO StockMovements (product_id, quantity, movement_type, movement_reason,
                                                    from_section_id, to_section_id, purchase_price)
                        VALUES (%s, %s, 'transfer', 'Переміщення між секціями', %s, %s, %s)
                    """, (item.product_id, item.quantity, current_section_id, section_id, None)) 

                # Оновлюємо секцію товару
                cursor.execute("""
                    UPDATE Products
                    SET section_id = %s
                    WHERE product_id = %s
                """, (section_id, item.product_id))

        connection.commit()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        connection.close()

def add_income_items_to_db(config, items: List):
    connection = get_db_connection(config)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            for item in items:
                # Перевірка, чи існує товар
                cursor.execute("SELECT * FROM Products WHERE product_id = %s", (item.product_id,))
                product = cursor.fetchone()
                if not product:
                    raise ValueError(f"Товар з ID {item.product_id} не знайдено.")

                # Перевірка секції
                cursor.execute("SELECT section_id FROM WarehouseSections WHERE name = %s", (item.section,))
                section = cursor.fetchone()
                if not section:
                    raise ValueError(f"Секція '{item.section}' не знайдена.")

                cursor.execute("""
                    INSERT INTO StockMovements (
                        product_id,
                        movement_type,
                        quantity,
                        from_section_id,
                        to_section_id,
                        movement_reason,
                        purchase_price
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    item.product_id,
                    "in",
                    item.quantity,
                    None,  # from_section_id
                    section["section_id"],  # to_section_id
                    "Надходження товару",
                    item.purchase_price
                ))

                cursor.execute("""
                    UPDATE Products
                    SET quantity = quantity + %s
                    WHERE product_id = %s
                """, (item.quantity, item.product_id))

        connection.commit()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        connection.close()


def get_stock_movements(config, page, limit, movement_type=None, product_id=None, section_id=None,
                        date_from=None, date_to=None, quantity_min=None, quantity_max=None):
    offset = (page - 1) * limit

    if movement_type == 'in':
        query = """
            SELECT 
                sm.movement_id,
                p.name AS product_name,
                sm.movement_type,
                sm.quantity,
                sm.movement_date,
                sm.purchase_price,
                ws.name AS section_name
            FROM StockMovements sm
            LEFT JOIN Products p ON sm.product_id = p.product_id
            LEFT JOIN WarehouseSections ws ON sm.to_section_id = ws.section_id
        """
    elif movement_type == 'out' or movement_type == 'write_off':
        # для списання та звичайного виходу з секції
        query = """
            SELECT 
                sm.movement_id,
                p.name AS product_name,
                sm.movement_type,
                sm.quantity,
                sm.movement_date,
                sm.movement_reason,
                ws.name AS section_name
            FROM StockMovements sm
            LEFT JOIN Products p ON sm.product_id = p.product_id
            LEFT JOIN WarehouseSections ws ON sm.from_section_id = ws.section_id
        """
    elif movement_type == 'transfer':
        query = """
            SELECT 
                sm.movement_id,
                p.name AS product_name,
                sm.movement_type,
                sm.quantity,
                sm.movement_date,
                ws_from.name AS from_section_name,
                ws_to.name AS to_section_name,
                sm.movement_reason
            FROM StockMovements sm
            LEFT JOIN Products p ON sm.product_id = p.product_id
            LEFT JOIN WarehouseSections ws_from ON sm.from_section_id = ws_from.section_id
            LEFT JOIN WarehouseSections ws_to ON sm.to_section_id = ws_to.section_id
        """
    else:
        raise ValueError("movement_type must be 'in', 'out', 'transfer', or 'write_off'")

    where_clauses = []
    params = []

    if movement_type:
        where_clauses.append("sm.movement_type = %s")
        params.append(movement_type)

    if product_id:
        where_clauses.append("sm.product_id = %s")
        params.append(product_id)

    if section_id:
        if movement_type in ('in',):
            where_clauses.append("sm.to_section_id = %s")
            params.append(section_id)
        elif movement_type in ('out', 'write_off'):
            where_clauses.append("sm.from_section_id = %s")
            params.append(section_id)
        elif movement_type == 'transfer':
            where_clauses.append("(sm.from_section_id = %s OR sm.to_section_id = %s)")
            params.extend([section_id, section_id])
        else:
            where_clauses.append("(sm.from_section_id = %s OR sm.to_section_id = %s)")
            params.extend([section_id, section_id])

    if date_from:
        where_clauses.append("sm.movement_date >= %s")
        params.append(date_from)

    if date_to:
        where_clauses.append("sm.movement_date <= %s")
        params.append(date_to)

    if quantity_min is not None:
        where_clauses.append("sm.quantity >= %s")
        params.append(quantity_min)

    if quantity_max is not None:
        where_clauses.append("sm.quantity <= %s")
        params.append(quantity_max)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY sm.movement_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def count_stock_movements(config, movement_type=None, product_id=None, section_id=None,
                          date_from=None, date_to=None, quantity_min=None, quantity_max=None):
    query = "SELECT COUNT(*) as total FROM StockMovements sm"

    where_clauses = []
    params = []

    if movement_type:
        where_clauses.append("sm.movement_type = %s")
        params.append(movement_type)

    if product_id:
        where_clauses.append("sm.product_id = %s")
        params.append(product_id)

    if section_id:
        if movement_type in ('in',):
            where_clauses.append("sm.to_section_id = %s")
            params.append(section_id)
        elif movement_type in ('out', 'write_off'):
            where_clauses.append("sm.from_section_id = %s")
            params.append(section_id)
        elif movement_type == 'transfer':
            where_clauses.append("(sm.from_section_id = %s OR sm.to_section_id = %s)")
            params.extend([section_id, section_id])
        else:
            where_clauses.append("(sm.from_section_id = %s OR sm.to_section_id = %s)")
            params.extend([section_id, section_id])

    if date_from:
        where_clauses.append("sm.movement_date >= %s")
        params.append(date_from)

    if date_to:
        where_clauses.append("sm.movement_date <= %s")
        params.append(date_to)

    if quantity_min is not None:
        where_clauses.append("sm.quantity >= %s")
        params.append(quantity_min)

    if quantity_max is not None:
        where_clauses.append("sm.quantity <= %s")
        params.append(quantity_max)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        connection.close()

def write_off_items_to_db(user_config: dict, items: list):
    """
    Записує товари на списання у StockMovements та зменшує кількість у Products.
    """
    connection = get_db_connection(user_config)
    try:
        cursor = connection.cursor()
        for item in items:
            # Перевірка доступної кількості
            cursor.execute("SELECT quantity FROM Products WHERE product_id=%s", (item.product_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Товар {item.product_id} не знайдено")
            available_qty = result[0]
            if available_qty < item.quantity:
                raise ValueError(f"Недостатньо кількості для продукту {item.product_id}")

            # Оновлення кількості у Products
            cursor.execute(
                "UPDATE Products SET quantity = quantity - %s WHERE product_id = %s",
                (item.quantity, item.product_id)
            )

            # Додавання запису у StockMovements
            cursor.execute(
                """
                INSERT INTO StockMovements
                (product_id, movement_type, quantity, movement_date, from_section_id, movement_reason)
                VALUES (%s, 'write_off', %s, NOW(), %s, %s)
                """,
                (item.product_id, item.quantity, item.section_id, item.reason)
            )
        connection.commit()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        cursor.close()
        connection.close()