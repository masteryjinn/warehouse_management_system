from config.config import DB_CONFIG_AUTH
import pymysql
from database.utils.connection_manager import get_db_connection

def get_user(username):
    query = """
    SELECT 
        u.password_hash, 
        u.role, 
        u.user_id, 
        u.is_temp_password, 
        e.name,
        ce.contact_value AS email
    FROM Users u
    LEFT JOIN Employees e ON u.employee_id = e.employee_id
    LEFT JOIN Contacts_employees ce ON e.employee_id = ce.employee_id AND ce.contact_type = 'email'
    WHERE u.username = %s
    LIMIT 1;
    """
    # Підключення до бази
    connection = pymysql.connect(**DB_CONFIG_AUTH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if user_data is None:
            return None

        return user_data

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_employee_id_by_user_id(user_id):
    query = """
    SELECT u.employee_id
    FROM Users u
    WHERE u.user_id = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_AUTH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, (user_id,))
        employee_id = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if employee_id is None:
            return None

        # Повертаємо перший елемент з кортежу
        return employee_id[0]

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_user_id_by_emp_id(emp_id):
    query = """
    SELECT u.user_id
    FROM Users u
    WHERE u.employee_id = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_AUTH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, (emp_id,))
        user_id = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if user_id is None:
            return None

        # Повертаємо перший елемент з кортежу
        return user_id[0]

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_user_id_and_role(username):
    query = """
    SELECT u.user_id, u.role
    FROM Users u
    WHERE u.username = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_AUTH)
    cursor = connection.cursor()
    try:
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if user_data is None:
            return None

        return {
            "user_id": user_data[0],
            "role": user_data[1]
        }
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_username_by_id(user_id):
    query = """
    SELECT u.username
    FROM Users u
    WHERE u.user_id = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_AUTH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, (user_id,))
        username = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if username is None:
            return None

        return username[0]

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_password_hash_by_user_id(user_id):
    query = """
    SELECT u.password_hash
    FROM Users u
    WHERE u.user_id = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_AUTH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, (user_id,))
        password_hash = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if password_hash is None:
            return None

        return password_hash[0]

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_username_by_emp_id(emp_id):
    query = """
    SELECT u.username
    FROM Users u
    WHERE u.employee_id = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_AUTH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, (emp_id,))
        username = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if username is None:
            return None

        return username[0]

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None

    finally:
        cursor.close()
        connection.close()

def get_user_auth_state_by_id(user_id):
    query = """
    SELECT u.is_temp_password
    FROM Users u
    WHERE u.user_id = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_AUTH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, (user_id,))
        is_temp_password = cursor.fetchone()

        # Перевірка, чи знайдено користувача
        if is_temp_password is None:
            return None

        return is_temp_password[0]

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return None

    finally:
        cursor.close()
        connection.close()
