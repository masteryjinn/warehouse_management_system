from database.utils.connection_manager import get_db_connection
from config.config import DB_CONFIG_ADMIN
import pymysql

role_mapping = {
        'admin': 'admin_role',
        'manager': 'manager_role',
        'employee': 'employee_role'
    }

def add_user_to_db(config, username, password_hash, emp_id, role):
    """
    Додає нового користувача до бази даних.
    Перевіряє, чи не існує користувач з таким username.
    :param config: Конфігурація бази даних
    :param username: Ім'я користувача
    :param password_hash: Хеш пароля
    :param emp_id: ID співробітника
    :param role: Роль користувача
    :return: True, якщо користувача успішно додано, False якщо ні або користувач існує
    """

    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Перевірка чи існує користувач із таким username
        check_query = "SELECT COUNT(*) FROM Users WHERE username = %s"
        cursor.execute(check_query, (username,))
        (count,) = cursor.fetchone()
        if count > 0:
            print("Користувач з таким ім'ям вже існує")
            return False

        # Якщо немає — вставляємо нового користувача
        insert_query = """
        INSERT INTO Users (username, password_hash, role, employee_id)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (username, password_hash, role, emp_id))
        connection.commit()
        return True

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()

def register_user_in_db(username: str, password_hash: str, role: str) -> bool:
    """
    Функція для реєстрації нового користувача в базі даних MySQL.
    :param username: Ім'я користувача
    :param password_hash: Хеш пароля
    :param role: Роль користувача
    :return: True, якщо користувача успішно зареєстровано, інакше False
    """
    connection = get_db_connection(DB_CONFIG_ADMIN)
    if connection is None:
        print("Не вдалося підключитися до бази даних")
        return False

    try:
        with connection.cursor() as cursor:
            safe_username = connection.escape_string(username)
            # Створення користувача в базі даних MySQL
            sql_create_user = f"CREATE USER '{safe_username}'@'%' IDENTIFIED BY '{password_hash}'"
            cursor.execute(sql_create_user)
            
            # Призначення ролі користувачу
            cursor.execute(f"GRANT {role_mapping.get(role, 'employee_role')} TO '{safe_username}'@'%'")
            cursor.execute(f"SET DEFAULT ROLE {role_mapping.get(role, 'employee_role')} TO '{safe_username}'@'%'")
        
        # Підтвердження змін
        connection.commit()
        print(f"Користувача '{safe_username}' успішно зареєстровано з роллю '{role}'")
        return True
    
    except pymysql.MySQLError as e:
        print(f"Помилка реєстрації користувача: {e}")
        connection.rollback()  # Відкат транзакції в разі помилки
        return False
    
    finally:
        connection.close()  # Закриваємо з'єднання з базою даних

# Функція для видалення користувача з бази даних
def delete_user_from_db( username: str) -> bool:
    try:
        # Підключення до бази даних
        connection = get_db_connection(DB_CONFIG_ADMIN)
        with connection.cursor() as cursor:
            # Скасовуємо привілеї користувача
            safe_username = connection.escape_string(username)
            cursor.execute(f"REVOKE ALL PRIVILEGES, GRANT OPTION FROM '{safe_username}'@'%'")
            
            # Видаляємо користувача з бази даних
            cursor.execute(f"DROP USER '{safe_username}'@'%'")
        
        # Підтверджуємо зміни
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error deleting user: {e}")
        connection.rollback()
        return False
    
    finally:
        connection.close()

def update_employee_function(config, emp_id, name, position, contacts: dict):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Оновлюємо основні дані працівника
        cursor.execute(
            "UPDATE Employees SET name=%s, position=%s WHERE employee_id=%s",
            (name, position, emp_id)
        )

        # Оновлюємо або додаємо контакти
        for contact_type, contact_value in contacts.items():
            if contact_value:
                # Перевіряємо, чи існує вже контакт цього типу
                cursor.execute("""
                    SELECT 1 FROM Contacts_employees
                    WHERE employee_id = %s AND contact_type = %s
                """, (emp_id, contact_type))

                if cursor.fetchone():
                    # Якщо є — оновлюємо
                    cursor.execute("""
                        UPDATE Contacts_employees
                        SET contact_value = %s
                        WHERE employee_id = %s AND contact_type = %s
                    """, (contact_value, emp_id, contact_type))
                else:
                    # Якщо нема — додаємо новий запис
                    cursor.execute("""
                        INSERT INTO Contacts_employees (employee_id, contact_type, contact_value)
                        VALUES (%s, %s, %s)
                    """, (emp_id, contact_type, contact_value))

        connection.commit()
        return True

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()


def delete_employee_function(config, emp_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Employees WHERE employee_id=%s", (emp_id,))
        connection.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def delete_employee_account_function(config, emp_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Users WHERE employee_id=%s", (emp_id,))
        connection.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def add_employee_function(config, name, position, contacts: dict):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO Employees (name, position) VALUES (%s, %s)", (name, position))
        emp_id = cursor.lastrowid

        for contact_type, contact_value in contacts.items():
            if contact_value:
                cursor.execute("""
                    INSERT INTO Contacts_employees (employee_id, contact_type, contact_value)
                    VALUES (%s, %s, %s)
                """, (emp_id, contact_type, contact_value))

        connection.commit()
        return emp_id
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()

def count_total_employees(config, search=None, registered_only=False):
    subquery = """
        SELECT 
            e.employee_id,
            e.name,
            e.position,
            MAX(CASE WHEN c.contact_type = 'email' THEN c.contact_value END) AS email,
            MAX(CASE WHEN c.contact_type = 'phone' THEN c.contact_value END) AS phone,
            MAX(CASE WHEN c.contact_type = 'address' THEN c.contact_value END) AS address
        FROM Employees e
        LEFT JOIN Contacts_employees c ON e.employee_id = c.employee_id
        LEFT JOIN Users u ON e.employee_id = u.employee_id
    """

    where_clauses = []
    having_clauses = []
    where_params = []
    having_params = []

    if registered_only:
        where_clauses.append("u.user_id IS NULL")

    if where_clauses:
        subquery += " WHERE " + " AND ".join(where_clauses)

    subquery += " GROUP BY e.employee_id"

    if search and search.strip():
        like = f"%{search.strip()}%"
        having_clauses.append("("
            "e.name LIKE %s OR "
            "e.position LIKE %s OR "
            "MAX(CASE WHEN c.contact_type = 'email' THEN c.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN c.contact_type = 'phone' THEN c.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN c.contact_type = 'address' THEN c.contact_value END) LIKE %s"
            ")")
        having_params.extend([like] * 5)

    if having_clauses:
        subquery += " HAVING " + " AND ".join(having_clauses)

    full_query = f"SELECT COUNT(*) AS total FROM ({subquery}) AS sub"
    query_params = where_params + having_params

    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute(full_query, query_params)
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        connection.close()

def get_employees_function(config, page, limit, search=None, registered_only=False):
    offset = (page - 1) * limit

    base_query = """
        SELECT 
            e.employee_id, 
            e.name, 
            e.position,
            MAX(CASE WHEN c.contact_type = 'email' THEN c.contact_value END) AS email,
            MAX(CASE WHEN c.contact_type = 'phone' THEN c.contact_value END) AS phone,
            MAX(CASE WHEN c.contact_type = 'address' THEN c.contact_value END) AS address,
            CASE 
                WHEN u.user_id IS NOT NULL THEN TRUE 
                ELSE FALSE 
            END AS is_registered
        FROM Employees e
        LEFT JOIN Contacts_employees c ON e.employee_id = c.employee_id
        LEFT JOIN Users u ON e.employee_id = u.employee_id
    """

    where_clauses = []
    having_clauses = []
    where_params = []
    having_params = []

    if registered_only:
        where_clauses.append("u.user_id IS NULL")

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += " GROUP BY e.employee_id"

    if search and search.strip():
        like = f"%{search.strip()}%"
        having_clauses.append("("
            "e.name LIKE %s OR "
            "e.position LIKE %s OR "
            "MAX(CASE WHEN c.contact_type = 'email' THEN c.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN c.contact_type = 'phone' THEN c.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN c.contact_type = 'address' THEN c.contact_value END) LIKE %s"
            ")")
        having_params.extend([like] * 5)

    if having_clauses:
        base_query += " HAVING " + " AND ".join(having_clauses)

    base_query += " ORDER BY e.employee_id LIMIT %s OFFSET %s"
    query_params = where_params + having_params + [limit, offset]

    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(base_query, query_params)
        return cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def update_user_role_in_db(config, emp_id, role):
    """
    Оновлює роль користувача в базі даних.
    :param config: Конфігурація бази даних
    :param emp_id: ID співробітника
    :param role: Нова роль
    :return: True, якщо роль успішно оновлено, інакше False
    """
    query = """
        UPDATE Users 
        SET role = %s 
        WHERE employee_id = %s
    """
    
    connection = get_db_connection(config)
    cursor = connection.cursor()
    
    try:
        cursor.execute(query, (role, emp_id))
        connection.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def grant_role_to_user(username, role):
    """
    Призначає роль користувачу в базі даних.
    :param config: Конфігурація бази даних
    :param username: Ім'я користувача
    :param role: Роль
    :return: True, якщо роль успішно призначено, інакше False
    """

    connection = get_db_connection(DB_CONFIG_ADMIN)
    cursor = connection.cursor()
    safe_username = connection.escape_string(username)
    query = f"GRANT {role_mapping.get(role, 'employee_role')} TO '{safe_username}'@'%'"
    
    try:
        cursor.execute(query)
        connection.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()
    
def get_employees_full(config):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("""SELECT 
            e.employee_id, 
            e.name, 
            e.position,
            MAX(CASE WHEN c.contact_type = 'email' THEN c.contact_value END) AS email,
            MAX(CASE WHEN c.contact_type = 'phone' THEN c.contact_value END) AS phone,
            MAX(CASE WHEN c.contact_type = 'address' THEN c.contact_value END) AS address
        FROM Employees e
        LEFT JOIN Contacts_employees c ON e.employee_id = c.employee_id
        GROUP BY e.employee_id
        """)

        return cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_employee_id_by_username(username):
    connection = get_db_connection(DB_CONFIG_ADMIN)
    cursor = connection.cursor()

    try:
        query = "SELECT employee_id FROM Users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            return result[0]
        return None
    finally:
        cursor.close()
        connection.close()

def get_employee_role_from_db(employee_id):
    connection = get_db_connection(DB_CONFIG_ADMIN)
    cursor = connection.cursor()

    try:
        query = "SELECT role FROM Users WHERE employee_id = %s"
        cursor.execute(query, (employee_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        return None
    finally:        
        cursor.close()
        connection.close()
    