from datetime import datetime, timedelta
from database.utils.connection_manager import get_db_connection

def check_unprocessed_orders(config):
    query = """
        SELECT order_id, order_date 
        FROM Orders
        WHERE status = 'new' AND order_date < %s
    """
    cutoff = datetime.now() - timedelta(days=1)
    connection = get_db_connection(config)
    cursor = connection.cursor()
    cursor.execute(query, (cutoff,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    notifications = []
    for order_id, order_date in rows:
        notifications.append({
            "title": "Нове замовлення без обробки",
            "message": f"Замовлення №{order_id} створено {order_date.strftime('%d.%m.%Y %H:%M')} і досі не оброблене.",
            "type": "info",
        })
    return notifications


def check_empty_orders(config):
    query = """
        SELECT o.order_id
        FROM Orders o
        LEFT JOIN OrderDetails od ON o.order_id = od.order_id
        WHERE od.order_id IS NULL
    """
    connection = get_db_connection(config)
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    notifications = []
    for (order_id,) in rows:
        notifications.append({
            "title": "Порожнє замовлення",
            "message": f"Замовлення №{order_id} не містить товарів. Перевірте та виправте.",
            "type": "error",
        })
    return notifications
