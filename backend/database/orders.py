import pymysql
from datetime import datetime, timedelta, date
from fastapi import HTTPException
from database.utils.connection_manager import get_db_connection

statuses = ["draft", "new", "collecting", "review_pack", "packed", "shipped", "restocking", "unpacking", "review_restock", "cancelled"]

def get_orders_function(config, page, limit, search=None, customer_name=None, status_filter=None, date_min=None, date_max=None):
    offset = (page - 1) * limit

    base_query = """
        SELECT 
            o.order_id,
            o.order_date,
            o.status,
            c.name AS customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
    """

    where_clauses = []
    params = []
    print("date_min =", repr(date_min))
    print("date_max =", repr(date_max))
    if search:
        like_val = f"%{search}%"
        where_clauses.append("(c.name LIKE %s OR o.order_id LIKE %s)")
        params.extend([like_val, like_val])

    if customer_name:
        where_clauses.append("c.name LIKE %s")
        params.append(f"%{customer_name}%")

    if status_filter:
        where_clauses.append("o.status = %s")
        params.append(status_filter)

    if date_min:
        where_clauses.append("o.order_date >= %s")
        params.append(date_min)

    if date_max:
        where_clauses.append("o.order_date <= %s")
        params.append(date_max)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += """
        ORDER BY o.order_id DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(base_query, params)
        print("SQL-запит:", base_query)
        print("Параметри:", params)
        return cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"MySQL error: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def count_total_orders(config, search=None, customer_name=None, status_filter=None, date_min=None, date_max=None):
    query = """
        SELECT COUNT(DISTINCT o.order_id) AS total
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
    """
    conditions = []
    params = []

    if search:
        like_val = f"%{search}%"
        conditions.append("(c.name LIKE %s OR o.order_id LIKE %s)")
        params.extend([like_val, like_val])

    if customer_name:
        conditions.append("c.name LIKE %s")
        params.append(f"%{customer_name}%")

    if status_filter:
        placeholders = ','.join(['%s'] * len(status_filter))
        conditions.append(f"o.status IN ({placeholders})")
        params.extend(status_filter)

    if date_min:
        conditions.append("o.order_date >= %s")
        params.append(date_min)

    if date_max:
        conditions.append("o.order_date <= %s")
        params.append(date_max)

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

def add_order_to_db(USER_CONFIG, customer_id):
    connection = get_db_connection(USER_CONFIG)
    cursor = connection.cursor()

    try:
        # Вставляємо нове замовлення до таблиці Orders
        cursor.execute("""
            INSERT INTO Orders (customer_id, status)
            VALUES (%s, 'draft')
        """, (customer_id,))

        connection.commit()
        return cursor.lastrowid  # Повертаємо ID нового замовлення

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")

    finally:
        cursor.close()
        connection.close()

def delete_orders_from_db(config, order_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Перевірка статусу замовлення
        cursor.execute("SELECT status FROM Orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Замовлення не знайдене.")

        status = result[0]
        if status == "shipped":
            raise HTTPException(status_code=400, detail="Виконані замовлення неможливо видалити.")

        # Видалення замовлення
        cursor.execute("""
            DELETE FROM Orders
            WHERE order_id = %s
        """, (order_id,))
        connection.commit()

        return {"message": "Замовлення успішно видалено."}

    except pymysql.MySQLError as err:
        connection.rollback()
        print(f"Помилка MySQL: {err}")
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")

    finally:
        cursor.close()
        connection.close()

def update_order_status_function(config, order_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Отримати поточний статус замовлення
        cursor.execute("SELECT status FROM Orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Замовлення не знайдено")

        current_status = result[0]

        # Перевірка наявності товарів у замовленні, якщо статус "new"
        if current_status == "draft":
            raise HTTPException(status_code=400, detail="Неможливо оновити статус замовлення, адже воно ще не підтверджене")
        if current_status == "new":
            cursor.execute("SELECT COUNT(*) FROM OrderDetails WHERE order_id = %s", (order_id,))
            details_count = cursor.fetchone()[0]

            if details_count == 0:
                raise HTTPException(status_code=400, detail="Неможливо перейти в статус обробки замовлення, адже воно порожнє")

            new_status = "processing"

        elif current_status in statuses:
            current_index = statuses.index(current_status)
            if current_index < len(statuses) - 1:
                new_status = statuses[current_index + 1]
            else:
                raise HTTPException(status_code=400, detail="Замовлення вже має кінцевий статус")

        # Оновлюємо статус
        cursor.execute("UPDATE Orders SET status = %s WHERE order_id = %s", (new_status, order_id))
        connection.commit()

        return new_status

    except pymysql.MySQLError as err:
        connection.rollback()
        print(f"Помилка MySQL: {err}")
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")

    finally:
        cursor.close()
        connection.close()


def calculate_smart_deadline(items, config):
    connection = get_db_connection(config)
    cursor = connection.cursor()
    
    # --- 1. Розрахунок чистого часу на ЦЕ замовлення ---
    unique_positions = len(items)
    total_quantity = sum(item.quantity for item in items)
    # Базовий час 30 хв + 5 хв на позицію + 2 хв на одиницю
    needed_minutes = 30 + (unique_positions * 5) + (total_quantity * 2)

    # --- 2. Визначаємо точку старту (Черга) ---
    # Шукаємо максимальний дедлайн серед усіх ще не виконаних завдань
    cursor.execute("""
        SELECT MAX(deadline) FROM tasks 
        WHERE status IN ('new', 'in_progress', 'under_review')
    """)
    row = cursor.fetchone()
    
    now = datetime.now()
    # Якщо в черзі нікого немає або останній дедлайн вже в минулому — стартуємо від "зараз"
    if row and row[0] and row[0] > now:
        start_point = row[0]
    else:
        start_point = now

    # --- 3. Додаємо час виконання до точки старту ---
    deadline = start_point + timedelta(minutes=needed_minutes)

    # --- 4. Коригування під робочий графік (09:00 - 18:00) ---
    work_start = 9
    work_end = 18

    # Якщо робота випадає на неробочий час (після 18:00)
    if deadline.hour >= work_end:
        # Рахуємо, скільки хвилин "вилізло" за межі 18:00
        day_end = deadline.replace(hour=work_end, minute=0, second=0)
        overtime_minutes = (deadline - day_end).total_seconds() / 60
        
        # Переносимо на наступний ранок (09:00 + залишок хвилин)
        deadline = (deadline + timedelta(days=1)).replace(hour=work_start, minute=0, second=0) + timedelta(minutes=overtime_minutes)

    # Якщо робота стартує до 09:00 (наприклад, замовлення вночі)
    if deadline.hour < work_start:
        deadline = deadline.replace(hour=work_start, minute=0, second=0) + timedelta(minutes=needed_minutes)

    cursor.close()
    connection.close()
    return deadline

def confirm_order_in_db(USER_CONFIG, order_id: int, items: list, user_id: int):
    connection = get_db_connection(USER_CONFIG)
    cursor = connection.cursor()

    try:
        # 1. Додаємо деталі замовлення
        for item in items:
            # ---- Перевірка терміну придатності ----
            cursor.execute("""
                SELECT name, expiration_date
                FROM Products
                WHERE product_id = %s
            """, (item.product_id,))
            product = cursor.fetchone()

            if product:
                product_name, expiration_date = product
                if expiration_date and expiration_date < date.today():
                    connection.rollback()  #  Відкат змін
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Замовлення #{order_id} не підтверджено. "
                            f"Товар '{product_name}' прострочений."
                        )
                    )

            # Додаємо деталі замовлення
            cursor.execute("""
                INSERT INTO OrderDetails (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item.product_id,
                item.quantity,
                item.price
            ))
    
        # 2. Оновлюємо статус замовлення
        cursor.execute("""
            UPDATE Orders
            SET status = 'new'
            WHERE order_id = %s
        """, (order_id,))

        # 3. Створюємо завдання для зборки замовлення
        # --- 3. Розрахунок параметрів завдання ---
        
        # Рахуємо загальну кількість одиниць товару в замовленні
        total_items_count = sum(item.quantity for item in items)
        
        # Визначаємо кількість виконавців (max_assignees)
        # Логіка: 1-10 од. = 1 людина, 11-20 од. = 2 людини, >20 од. = 3 людини
        if total_items_count > 20:
            suggested_assignees = 3
            priority = 'high' # Велике замовлення — високий пріоритет
        elif total_items_count > 10:
            suggested_assignees = 2
            priority = 'medium'
        else:
            suggested_assignees = 1
            priority = 'low'

        task_deadline = calculate_smart_deadline(items, USER_CONFIG)
        
        task_query = """
            INSERT INTO tasks (
                title, description, priority, status, 
                created_by, deadline, max_assignees, order_id, task_type
            )
            VALUES (%s, %s, %s, 'new', %s, %s, %s, %s, 'pack')
        """
        
        description = (
            f"Необхідно зібрати товари для замовлення №{order_id}. "
            f"Загальна кількість одиниць: {total_items_count}."
        )

        cursor.execute(task_query, (
            f"Збірка замовлення #{order_id}",
            description,
            priority,       # Динамічний пріоритет
            user_id,
            task_deadline,
            suggested_assignees, # Динамічна кількість людей
            order_id
        ))
        
        # 4. Фіксуємо зміни в базі даних
        connection.commit()

    except pymysql.MySQLError as err:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")

    finally:
        cursor.close()
        connection.close()

def get_order_details_from_db(config, order_id):
    query = query = """
        SELECT 
            o.order_id,
            o.order_date,
            cust.name AS customer_name,
            p.name AS product_name,
            od.quantity,
            p.unit,
            od.price,
            (od.quantity * od.price) AS line_total,
            s.name AS section_name
        FROM OrderDetails od
        JOIN Orders o ON od.order_id = o.order_id
        JOIN Customers cust ON o.customer_id = cust.customer_id
        JOIN Products p ON od.product_id = p.product_id
        LEFT JOIN WarehouseSections s ON p.section_id = s.section_id
        WHERE od.order_id = %s
        ORDER BY s.name ASC;
    """
    try:
        print(f"[DEBUG] Отримуємо деталі для замовлення ID = {order_id}")
        connection = get_db_connection(config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, (order_id,))
        items = cursor.fetchall()
        print(f"[DEBUG] Отримано {len(items)} записів із бази даних")
        return items

    except Exception as err:
        print(f"[ERROR] Помилка при отриманні деталей замовлення: {err}")
        raise HTTPException(status_code=500, detail=f"Помилка сервера: {err}")

    finally:
        cursor.close()
        connection.close()
        
def get_invoice_data_from_db(config, order_id):
    query = """
        SELECT 
            o.order_id,
            o.order_date,
            c.name AS customer_name,
            -- Отримуємо телефон
            (SELECT contact_value FROM Contacts_customers 
             WHERE customer_id = c.customer_id AND contact_type = 'phone' LIMIT 1) AS phone,
            -- Отримуємо адресу
            (SELECT contact_value FROM Contacts_customers 
             WHERE customer_id = c.customer_id AND contact_type = 'address' LIMIT 1) AS address,
            -- Отримуємо електронну пошту
            (SELECT contact_value FROM Contacts_customers
                WHERE customer_id = c.customer_id AND contact_type = 'email' LIMIT 1) AS email,
            p.name AS product_name,
            od.quantity,
            p.unit,
            od.price,
            cat.name AS category_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN OrderDetails od ON o.order_id = od.order_id
        JOIN Products p ON od.product_id = p.product_id
        LEFT JOIN ProductCategories cat ON p.category_id = cat.category_id
        WHERE o.order_id = %s
    """
    try:
        connection = get_db_connection(config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, (order_id,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"[ERROR] Помилка отримання даних: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def bulk_ship_orders_in_db(config, order_ids):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Оновлюємо статус замовлень на 'shipped'
        format_strings = ','.join(['%s'] * len(order_ids))
        cursor.execute(f"""
            UPDATE Orders
            SET status = 'shipped'
            WHERE order_id IN ({format_strings})
        """, tuple(order_ids))

        # Фіксуємо відвантаження
        movement_query = f"""
            INSERT INTO StockMovements (product_id, movement_type, quantity, from_section_id, movement_reason)
            SELECT od.product_id, 'out', od.quantity, p.section_id, 
                   CONCAT('Масове відвантаження. Замовлення #', od.order_id)
            FROM OrderDetails od
            JOIN Products p ON od.product_id = p.product_id
            WHERE od.order_id IN ({format_strings})
        """
        cursor.execute(movement_query, tuple(order_ids))
        connection.commit()
    except pymysql.MySQLError as err:
        connection.rollback()
        print(f"Помилка MySQL: {err}")
        raise HTTPException(status_code=500, detail=f"Помилка бази даних: {err}")
    finally:
        cursor.close()
        connection.close()

def cancel_order_in_db(config, order_id, user_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # 1. Отримуємо поточний статус замовлення
        cursor.execute("SELECT status FROM Orders WHERE order_id = %s", (order_id,))
        row = cursor.fetchone()
        if not row:
            return False
        current_status = row[0]

        # Якщо замовлення вже відправлено або скасовано — нічого не робимо
        if current_status in ['shipped', 'cancelled']:
            return False

        # 2. ЛОГІКА СКАСУВАННЯ ЗАЛЕЖНО ВІД СТАТУСУ
        
        # А. Якщо замовлення "Нове" (товар заброньовано, але завдання ще не в роботі)
        if current_status == 'new':
            # Скасовуємо всі активні завдання на збірку
            cursor.execute("""
                UPDATE tasks SET status = 'cancelled' 
                WHERE order_id = %s AND task_type = 'pack' AND status = 'new'
            """, (order_id,))

            # Повертаємо товар на склад (збільшуємо quantity)
            cursor.execute("""
                UPDATE Products p
                JOIN OrderDetails od ON p.product_id = od.product_id
                SET p.quantity = p.quantity + od.quantity
                WHERE od.order_id = %s
            """, (order_id,))

            # Ставимо фінальний статус
            cursor.execute("UPDATE Orders SET status = 'cancelled' WHERE order_id = %s", (order_id,))

        # Б. Якщо товар вже збирається, перевіряється або упакований
        elif current_status in ['collecting', 'review_pack', 'packed']:
            # 1. Скасовуємо поточні завдання на збірку (якщо вони були in_progress/under_review)
            cursor.execute("""
                UPDATE tasks SET status = 'cancelled' 
                WHERE order_id = %s AND task_type = 'pack' AND status != 'completed'
            """, (order_id,))

            # 2. Створюємо завдання на РОЗПАКУВАННЯ (restock)
            # Ми не повертаємо товар на склад тут, це зробить працівник після завершення Task
            cursor.execute("""
                INSERT INTO tasks (title, description, priority, status, created_by, order_id, task_type, max_assignees)
                VALUES (%s, %s, 'high', 'new', %s, %s, 'restock', 1)
            """, (
                f"Розпакування скасованого замовлення #{order_id}",
                f"Замовлення було скасовано на етапі {current_status}. Поверніть товари на полиці.",
                user_id,
                order_id
            ))

            # 3. Змінюємо статус на "Очікує розпакування"
            cursor.execute("UPDATE Orders SET status = 'restocking' WHERE order_id = %s", (order_id,))

        # В. Якщо це була чернетка
        elif current_status == 'draft':
            cursor.execute("UPDATE Orders SET status = 'cancelled' WHERE order_id = %s", (order_id,))

        connection.commit()
        return True

    except Exception as e:
        print(f"Error cancelling order: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
        