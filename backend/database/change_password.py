from config.config import DB_CONFIG_ADMIN, DB_CONFIG_CHANGE_PASSWORD
import pymysql
from database.utils.connection_manager import get_db_connection

# Функція для отримання айді працівника за email
def get_employee_id_by_email(email):
    query = """
    SELECT c.employee_id
    FROM Contacts_employees c
    WHERE c.contact_type = 'email' AND c.contact_value = %s
    """
    # Підключення до бази
    connection = get_db_connection(DB_CONFIG_CHANGE_PASSWORD) 
    cursor = connection.cursor()

    try:
        cursor.execute(query, (email,))
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

def perform_password_reset(username, new_password_hash):
    connection = get_db_connection(DB_CONFIG_CHANGE_PASSWORD)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        query_update = """
        UPDATE Users
        SET password_hash = %s, is_temp_password = TRUE
        WHERE username = %s
        """
        cursor.execute(query_update, (new_password_hash, username))
        connection.commit()

        print("Пароль успішно змінено.")
        return True

    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()


def update_user_password(username, new_password_hash):
    """Оновлює пароль у Users і MySQL (якщо користувач існує)"""
    
    # SQL-запит для оновлення пароля в Users
    user_update_query = """
    UPDATE Users
    SET password_hash = %s, is_temp_password = FALSE
    WHERE username = %s
    """

    # SQL-запит для перевірки існування користувача у MySQL
    check_user_query = "SELECT COUNT(*) FROM mysql.user WHERE user = %s"

    # SQL-запит для зміни пароля користувача у MySQL
    alter_user_query = f"ALTER USER %s@'localhost' IDENTIFIED BY %s"

    connection = get_db_connection(DB_CONFIG_ADMIN)
    cursor = connection.cursor()

    try:
        # Оновлення пароля у таблиці Users
        cursor.execute(user_update_query, (new_password_hash, username))

        # Перевірка існування користувача в MySQL
        cursor.execute(check_user_query, (username,))
        user_exists = cursor.fetchone()[0]

        if user_exists:
            # Зміна пароля в MySQL
            cursor.execute(alter_user_query, (username, new_password_hash))
        
        connection.commit()
        return {"success": True, "message": "Пароль успішно змінено"}

    except pymysql.MySQLError as err:
        connection.rollback()
        return {"success": False, "message": f"Помилка MySQL: {err}"}

    finally:
        cursor.close()
        connection.close()

