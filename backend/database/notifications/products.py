from datetime import date
from database.utils.connection_manager import get_db_connection

def check_low_stock_products(config):
    query = """
        SELECT product_id, name, quantity 
        FROM Products
        WHERE quantity < 5
    """
    connection = get_db_connection(config)
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    notifications = []
    for product_id, name, quantity in rows:
        notifications.append({
            "title": "Низький запас товару",
            "message": f"Товар '{name}' має залишок {quantity} одиниць. Рекомендується поповнити запаси.",
            "type": "warning"
        })
    return notifications


def check_expired_products(config):
    query = """
        SELECT product_id, name, expiration_date 
        FROM Products
        WHERE expiration_date IS NOT NULL AND expiration_date < %s
    """
    today = date.today()
    connection = get_db_connection(config)
    cursor = connection.cursor()
    cursor.execute(query, (today,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    notifications = []
    for product_id, name, expiration_date in rows:
        notifications.append({
            "title": "Протермінований товар",
            "message": f"Товар '{name}' прострочений (термін закінчився {expiration_date}). Рекомендується списати або утилізувати.",
            "type": "error"
        })
    return notifications
