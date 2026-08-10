# db/reports.py
import pymysql
from database.utils.connection_manager import get_db_connection

def get_report_data(config, start_date, end_date, status, category=None):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT 
            DATE(o.order_date) AS date,
            COUNT(DISTINCT o.order_id) AS total_orders,
            SUM(od.quantity) AS total_items,
            SUM(od.quantity * od.price) AS total_revenue
        FROM Orders o
        JOIN OrderDetails od ON o.order_id = od.order_id
        JOIN Products p ON od.product_id = p.product_id
        LEFT JOIN ProductCategories pc ON p.category_id = pc.category_id
        WHERE o.order_date BETWEEN %s AND %s
        AND o.status = %s
    """
    params = [start_date, end_date, status]
    if category and category != "Усі категорії":
        query += " AND pc.name = %s"
        params.append(category)

    query += " GROUP BY DATE(o.order_date) ORDER BY date;"

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        report_data = rows
        # Ось тут ми використовуємо ключі для доступу до значень у словниках
        total_orders = sum(row['total_orders'] for row in report_data)
        total_items = sum(row['total_items'] for row in report_data)
        total_revenue = sum(row['total_revenue'] for row in report_data)
        return rows, total_orders, total_items, total_revenue
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return [], 0, 0, 0
    finally:
        cursor.close()
        connection.close()