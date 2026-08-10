from datetime import datetime, timedelta
from database.utils.connection_manager import get_db_connection

def check_stale_orders(config):
    query = """
        SELECT o.order_id, osh.changed_at
        FROM Orders o
        JOIN (
            SELECT order_id, MAX(changed_at) as changed_at
            FROM OrderStatusHistory
            GROUP BY order_id
        ) osh ON o.order_id = osh.order_id
        WHERE osh.changed_at < %s AND o.status != 'shipped' AND o.status != 'cancelled'
    """
    cutoff = datetime.now() - timedelta(days=3)
    connection = get_db_connection(config)
    cursor = connection.cursor()
    cursor.execute(query, (cutoff,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    notifications = []
    for order_id, changed_at in rows:
        notifications.append({
            "title": "Замовлення довго не оновлювалося",
            "message": f"Статус замовлення №{order_id} не змінювався з {changed_at.strftime('%d.%m.%Y %H:%M')}.",
            "type": "warning",
        })
    return notifications
