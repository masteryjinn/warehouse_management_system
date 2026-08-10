import pymysql
from database.utils.connection_manager import get_db_connection 

def get_tasks(config, page, page_size, status=None, status_tab=None,
              priority=None, employee_id=None,
              start_date=None, end_date=None, search=None):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    try:
        where_clauses = []
        params = []

        # Фільтр по вкладці статусу
        if status_tab == "active":
            where_clauses.append("t.status IN ('new', 'in_progress', 'under_review')")
        elif status_tab == "archived":
            where_clauses.append("t.status IN ('completed', 'cancelled')")

        # Фільтр по конкретному статусу
        if status:
            where_clauses.append("t.status = %s")
            params.append(status)

        # Фільтр по пріоритету
        if priority:
            where_clauses.append("t.priority = %s")
            params.append(priority)

        # Фільтр по виконавцю
        if employee_id:
            where_clauses.append("""
                EXISTS (
                    SELECT 1 FROM task_assignments ta
                    JOIN Users u2 ON ta.user_id = u2.user_id
                    WHERE ta.task_id = t.task_id AND u2.employee_id = %s
                )
            """)
            params.append(employee_id)

        # Фільтр по даті початку
        if start_date:
            where_clauses.append("DATE(t.created_at) >= %s")
            params.append(start_date)

        # Фільтр по даті завершення
        if end_date:
            where_clauses.append("DATE(t.created_at) <= %s")
            params.append(end_date)

        # Пошук по назві
        if search:
            where_clauses.append("t.title LIKE %s")
            params.append(f"%{search}%")

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        # Підрахунок загальної кількості
        count_query = f"SELECT COUNT(*) as cnt FROM tasks t {where_sql}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()["cnt"]

        # Пагінація
        offset = (page - 1) * page_size

        # Основний запит
        query = f"""
        SELECT
            t.task_id,
            t.title,
            t.description,
            t.priority,
            t.status,
            t.created_by,
            e_creator.name AS creator_name,
            DATE_FORMAT(t.deadline, '%%Y-%%m-%%d %%H:%%i') AS deadline,
            t.max_assignees,

            -- підрахунок кількості вже призначених виконавців
            (SELECT COUNT(*) FROM task_assignments ta WHERE ta.task_id = t.task_id) AS assigned_count,

            -- список виконавців у JSON
            (SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'user_id', ta.user_id,
                    'name', e_assignee.name
                )
            )
             FROM task_assignments ta
             JOIN Users u2 ON ta.user_id = u2.user_id
             JOIN Employees e_assignee ON u2.employee_id = e_assignee.employee_id
             WHERE ta.task_id = t.task_id
            ) AS assignees

        FROM tasks t
        JOIN Users u ON t.created_by = u.user_id
        JOIN Employees e_creator ON u.employee_id = e_creator.employee_id
        {where_sql}
        ORDER BY t.created_at DESC
        LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [page_size, offset])
        tasks = cursor.fetchall()

        # Обробка JSON-списків
        import json
        for task in tasks:
            if task['assignees'] is None:
                task['assignees'] = []
            else:
                task['assignees'] = json.loads(task['assignees'])

        return tasks, total_count

    except pymysql.MySQLError as e:
        print(f"Error fetching tasks: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def create_task_in_db(config, task_data, user_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()
    print(task_data.deadline)
    try:
        query = """
        INSERT INTO tasks (title, description, priority, status, created_by, deadline, max_assignees)
        VALUES (%s, %s, %s, 'new', %s, %s, %s)
        """
        cursor.execute(query, (
            task_data.title,
            task_data.description or '',
            task_data.priority,
            user_id,
            task_data.deadline,
            task_data.max_assignees
        ))
        connection.commit()
        return cursor.lastrowid

    except pymysql.MySQLError as e:
        print(f"Error creating task: {e}")
        connection.rollback()
        return None

    finally:
        cursor.close()
        connection.close()

def update_task_status_in_db(config, task_id, new_status):
    connection = get_db_connection(config)
    cursor = connection.cursor()
    try:
        # Отримуємо тип та order_id
        cursor.execute("SELECT order_id, task_type FROM tasks WHERE task_id = %s", (task_id,))
        task_row = cursor.fetchone()
        if not task_row: return False
        order_id, task_type = task_row

        # 1. Оновлюємо статус самого завдання (це робимо ЗАВЖДИ)
        cursor.execute("UPDATE tasks SET status = %s WHERE task_id = %s", (new_status, task_id))

        # 2. А логіку замовлень виконуємо ТІЛЬКИ якщо order_id існує
        if order_id:
            if new_status == "under_review":
                if task_type == 'pack':
                    # Переводимо замовлення на перевірку пакування
                    cursor.execute("UPDATE Orders SET status = 'review_pack' WHERE order_id = %s", (order_id,))
                    
                    # РУХ ТОВАРУ: З полиць у зону пакування
                    cursor.execute("SELECT section_id FROM WarehouseSections WHERE section_type = 'packaging' LIMIT 1")
                    sect_row = cursor.fetchone()
                    if not sect_row:
                        raise Exception("Секція пакування не знайдена")
                    
                    packaging_section_id = sect_row[0]
                    reason = f"Збірка замовлення #{order_id} (на перевірку)"
                    
                    movement_query = """
                        INSERT INTO StockMovements (product_id, movement_type, quantity, from_section_id, to_section_id, movement_reason)
                        SELECT od.product_id, 'transfer', od.quantity, p.section_id, %s, %s
                        FROM OrderDetails od
                        JOIN Products p ON od.product_id = p.product_id
                        WHERE od.order_id = %s
                    """
                    cursor.execute(movement_query, (packaging_section_id, reason, order_id))
                elif task_type == 'restock':
                    cursor.execute("UPDATE Orders SET status = 'review_restock' WHERE order_id = %s", (order_id,))

            elif new_status == "completed":
                if task_type == 'pack':
                    cursor.execute("UPDATE Orders SET status = 'packed' WHERE order_id = %s", (order_id,))
                elif task_type == 'restock':
                    # Повернення товару
                    update_stock_query = """
                        UPDATE Products p
                        JOIN OrderDetails od ON p.product_id = od.product_id
                        SET p.quantity = p.quantity + od.quantity
                        WHERE od.order_id = %s
                    """
                    cursor.execute(update_stock_query, (order_id,))
                    cursor.execute("UPDATE Orders SET status = 'cancelled' WHERE order_id = %s", (order_id,))
                
                cursor.execute("UPDATE Task_Assignments ta JOIN Users u ON ta.user_id = u.user_id JOIN Employees e ON u.employee_id = e.employee_id SET ta.status = 'done' WHERE ta.task_id = %s", (task_id,))

        connection.commit()
        return True
    
    except pymysql.MySQLError as e:
        print(f"Error updating task status: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def assign_task_to_user(config, task_id, user_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()
    try:
        # 1. Отримуємо дані про завдання (order_id та тип завдання)
        cursor.execute("SELECT order_id, task_type, max_assignees FROM tasks WHERE task_id=%s", (task_id,))
        task = cursor.fetchone()
        if not task:
            return False
        order_id, task_type, max_assignees = task

        # 2. Перевіряємо, чи користувач вже призначений
        cursor.execute("SELECT COUNT(*) FROM task_assignments WHERE task_id=%s AND user_id=%s", (task_id, user_id))
        (count,) = cursor.fetchone()
        if count > 0:
            return False 

        # 3. Перевіряємо ліміт виконавців
        cursor.execute("SELECT COUNT(*) FROM task_assignments WHERE task_id=%s", (task_id,))
        (assigned_count,) = cursor.fetchone()
        if assigned_count >= (max_assignees or 1):
            return False 

        # 4. Додаємо виконавця
        cursor.execute("INSERT INTO task_assignments (task_id, user_id) VALUES (%s, %s)", (task_id, user_id))

        # 5. Змінюємо статус замовлення
        if order_id:
            # Якщо це 'pack' -> 'collecting', якщо 'restock' -> 'unpacking'
            new_status = 'collecting' if task_type == 'pack' else 'unpacking'
            cursor.execute("UPDATE Orders SET status=%s WHERE order_id=%s", (new_status, order_id))

        connection.commit()
        return True

    except Exception as e:
        print(f"Error assigning task: {e}")
        connection.rollback()
        return False
    except pymysql.MySQLError as e:
        print(f"MySQL error assigning task: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def unassign_task_from_user(config, task_id, user_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()
    try:
        # 1. Отримуємо дані про завдання
        cursor.execute("SELECT order_id, task_type FROM tasks WHERE task_id=%s", (task_id,))
        task = cursor.fetchone()
        if not task:
            return False
        order_id, task_type = task

        # 2. Видаляємо виконавця
        cursor.execute("DELETE FROM task_assignments WHERE task_id=%s AND user_id=%s", (task_id, user_id))
        
        # 3. Перевіряємо, чи залишилися ще виконавці
        cursor.execute("SELECT COUNT(*) FROM task_assignments WHERE task_id=%s", (task_id,))
        (remaining_count,) = cursor.fetchone()

        if remaining_count == 0 and order_id:
            # Якщо виконавців більше немає, повертаємо статус "на початок"
            # Якщо 'pack' -> 'new', якщо 'restock' -> 'restocking'
            revert_status = 'new' if task_type == 'pack' else 'restocking'
            cursor.execute("UPDATE Orders SET status=%s WHERE order_id=%s", (revert_status, order_id))

        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error unassigning task: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def is_user_assigned_to_task(config, task_id: int, user_id: int) -> bool:
    import pymysql
    connection = get_db_connection(config)
    cursor = connection.cursor()
    try:
        query = """
        SELECT COUNT(*) FROM task_assignments 
        WHERE task_id = %s AND user_id = %s
        """
        cursor.execute(query, (task_id, user_id))
        (count,) = cursor.fetchone()
        return count > 0
    except pymysql.MySQLError as e:
        print(f"Error checking task assignment: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def delete_task_from_db(config, task_id):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT order_id FROM tasks WHERE task_id = %s", (task_id,))
        task = cursor.fetchone()

        if not task:
            return False

        if task['order_id'] is not None:
            # Піднімаємо помилку, яку потім обробить роутер
            raise ValueError(f"Неможливо видалити завдання, бо воно прив'язане до замовлення #{task['order_id']}")

        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        connection.close()