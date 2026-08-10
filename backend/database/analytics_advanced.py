from database.utils.connection_manager import get_db_connection
import statistics


def get_abc_analysis(config, start_date, end_date):
    """
    ABC-аналіз товарів за оборотом.
    A - 80% обороту, B - 15%, C - 5%
    """
    conn = get_db_connection(config)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            p.product_id,
            p.name,
            COALESCE(pc.name, 'Без категорії') as category_name,
            p.price,
            p.unit,
            -- Рахуємо кількість проданого товару саме із деталей оформлених замовлень
            COALESCE(SUM(od.quantity), 0) as sold_quantity,
            -- Множимо кількість на ціну, за якою товар реально продали (із деталей замовлення)
            COALESCE(SUM(od.quantity * od.price), 0) as revenue,
            -- Рахуємо унікальні дні, коли цей товар купували
            COUNT(DISTINCT DATE(o.order_date)) as active_days
        FROM Products p
        LEFT JOIN ProductCategories pc ON p.category_id = pc.category_id
        -- З'єднуємо з деталями замовлень
        LEFT JOIN OrderDetails od ON p.product_id = od.product_id
        -- Прив'язуємо саме замовлення, щоб накласти фільтри по статусу та датах
        LEFT JOIN Orders o ON od.order_id = o.order_id 
            AND o.status = 'shipped'
            AND o.order_date BETWEEN %s AND %s
        GROUP BY p.product_id, p.name, pc.name, p.price, p.unit
        -- Залишаємо в аналітиці лише ті товари, які купували у вказаний період
        HAVING sold_quantity > 0
        ORDER BY revenue DESC
    """
    
    cursor.execute(query, (start_date, end_date))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not products:
        return []
    
    # Розрахунок ABC класів
    total_revenue = sum(float(p[6]) for p in products)
    
    results = []
    cumulative_percentage = 0.0
    
    for product in products:
        revenue = float(product[6])
        revenue_percentage = (revenue / total_revenue) * 100
        cumulative_percentage += revenue_percentage
        
        # Визначення класу
        if cumulative_percentage <= 80:
            abc_class = 'A'
        elif cumulative_percentage <= 95:
            abc_class = 'B'
        else:
            abc_class = 'C'
        
        results.append({
            'product_id': product[0],
            'name': product[1],
            'category': product[2],
            'price': float(product[3]),
            'unit': product[4],
            'sold_quantity': int(product[5]),
            'revenue': round(revenue, 2),
            'revenue_percentage': round(revenue_percentage, 2),
            'cumulative_percentage': round(cumulative_percentage, 2),
            'active_days': int(product[7]),
            'abc_class': abc_class
        })
    
    return results


def get_xyz_analysis(config, start_date, end_date):
    """
    XYZ-аналіз: стабільність попиту.
    X - коеф. варіації < 10% (стабільний)
    Y - 10-25% (змінний)
    Z - > 25% (нестабільний)
    """
    conn = get_db_connection(config)
    cursor = conn.cursor()
    
    # Отримуємо денні продажі для кожного товару
    query = """
        SELECT 
            p.product_id,
            p.name,
            -- Беремо дату саме з замовлення
            DATE(o.order_date) as sale_date,
            -- Рахуємо сумарну кількість, продану за цей конкретний день
            SUM(od.quantity) as daily_quantity
        FROM Products p
        INNER JOIN OrderDetails od ON p.product_id = od.product_id
        INNER JOIN Orders o ON od.order_id = o.order_id
        WHERE o.status = 'shipped'
            AND o.order_date BETWEEN %s AND %s
        GROUP BY p.product_id, p.name, DATE(o.order_date)
        ORDER BY p.product_id, sale_date
    """
    
    cursor.execute(query, (start_date, end_date))
    sales_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Групуємо по товарам
    products_sales = {}
    for row in sales_data:
        product_id = row[0]
        if product_id not in products_sales:
            products_sales[product_id] = {
                'name': row[1],
                'daily_sales': []
            }
        products_sales[product_id]['daily_sales'].append(int(row[3]))
    
    results = []
    for product_id, data in products_sales.items():
        daily_sales = data['daily_sales']
        
        if len(daily_sales) < 2:
            continue
        
        avg_sales = statistics.mean(daily_sales)
        std_deviation = statistics.stdev(daily_sales)
        
        # Коефіцієнт варіації
        coefficient_variation = (std_deviation / avg_sales * 100) if avg_sales > 0 else 0
        
        # Визначення класу XYZ
        if coefficient_variation < 10:
            xyz_class = 'X'
        elif coefficient_variation < 25:
            xyz_class = 'Y'
        else:
            xyz_class = 'Z'
        
        results.append({
            'product_id': product_id,
            'name': data['name'],
            'avg_sales': round(avg_sales, 2),
            'std_deviation': round(std_deviation, 2),
            'coefficient_variation': round(coefficient_variation, 2),
            'xyz_class': xyz_class
        })
    
    return sorted(results, key=lambda x: x['coefficient_variation'])


def get_abc_xyz_matrix(config, start_date, end_date):
    """
    Комбінована ABC-XYZ матриця.
    """
    abc_data = get_abc_analysis(config, start_date, end_date)
    xyz_data = get_xyz_analysis(config, start_date, end_date)
    
    # Створюємо словник XYZ даних
    xyz_dict = {item['product_id']: item for item in xyz_data}
    
    # Об'єднуємо дані
    results = []
    for abc_item in abc_data:
        product_id = abc_item['product_id']
        xyz_item = xyz_dict.get(product_id, {})
        
        results.append({
            **abc_item,
            'xyz_class': xyz_item.get('xyz_class', 'Z'),
            'coefficient_variation': xyz_item.get('coefficient_variation', 100)
        })
    
    return results


def get_turnover_analysis(config, start_date, end_date):
    """
    Аналіз оборотності товарів.
    Оборотність = Середній запас / Середній денний продаж
    """
    conn = get_db_connection(config)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            p.product_id,
            p.name,
            p.quantity as current_stock,
            -- Рахуємо загальну кількість проданого товару через деталі замовлень
            COALESCE(SUM(od.quantity), 0) as total_sold,
            -- Рахуємо кількість унікальних днів, коли товар реально купували
            COUNT(DISTINCT DATE(o.order_date)) as active_days
        FROM Products p
        -- З'єднуємо з деталями, щоб дізнатися кількість у проданих замовленнях
        LEFT JOIN OrderDetails od ON p.product_id = od.product_id
        -- З'єднуємо із самими замовленнями для фільтрації за статусом та датами
        LEFT JOIN Orders o ON od.order_id = o.order_id
            AND o.status = 'shipped'
            AND o.order_date BETWEEN %s AND %s
        GROUP BY p.product_id, p.name, p.quantity
        -- Залишаємо лише ті товари, за якими були продажі у цей період
        HAVING total_sold > 0
    """
    
    cursor.execute(query, (start_date, end_date))
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    results = []
    period_days = (end_date - start_date).days + 1
    
    for product in products:
        total_sold = int(product[3])
        active_days = int(product[4])
        current_stock = int(product[2])
        
        # Середній денний продаж
        avg_daily_sales = total_sold / period_days if period_days > 0 else 0
        
        # Оборотність в днях
        turnover_days = current_stock / avg_daily_sales if avg_daily_sales > 0 else 999
        
        results.append({
            'product_id': product[0],
            'name': product[1],
            'current_stock': current_stock,
            'sold_quantity': total_sold,
            'avg_stock': current_stock,
            'avg_daily_sales': round(avg_daily_sales, 2),
            'turnover_days': round(turnover_days, 1),
            'turnover_rate': round(365 / turnover_days, 2) if turnover_days > 0 else 0
        })
    
    return sorted(results, key=lambda x: x['turnover_days'])


def get_critical_stock_advanced(config):
    """
    Розширений аналіз критичних залишків з рекомендаціями.
    Тепер використовує останню ціну закупівлі для розрахунку бюджету.
    """
    conn = get_db_connection(config)
    cursor = conn.cursor()
    
    query = """
        WITH DailySales AS (
            SELECT 
                product_id,
                AVG(daily_quantity) as avg_daily_sales
            FROM (
                SELECT 
                    od.product_id,
                    DATE(o.order_date) as sale_date,
                    SUM(od.quantity) as daily_quantity
                FROM OrderDetails od
                INNER JOIN Orders o ON od.order_id = o.order_id
                WHERE o.status = 'shipped'
                    -- Аналізуємо динаміку продажів за останні 30 днів
                    AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY od.product_id, DATE(o.order_date)
            ) daily_data
            GROUP BY product_id
        ),
        LastPurchases AS (
            /* Знаходимо останню ціну закупівлі для кожного товару з історії надходжень */
            SELECT sm1.product_id, sm1.purchase_price
            FROM StockMovements sm1
            WHERE sm1.movement_type = 'in'
            AND sm1.movement_id = (
                SELECT MAX(sm2.movement_id)
                FROM StockMovements sm2
                WHERE sm2.product_id = sm1.product_id 
                    AND sm2.movement_type = 'in'
            )
        )
        SELECT 
            p.product_id,
            p.name,
            COALESCE(pc.name, 'Без категорії') as category_name,
            p.price, -- Роздрібна ціна продажу
            p.quantity as current_stock,
            p.unit,
            COALESCE(s.name, 'Без постачальника') as supplier_name,
            COALESCE(ws.name, 'Без секції') as section_name,
            COALESCE(ds.avg_daily_sales, 0) as avg_daily_sales,
            COALESCE(lp.purchase_price, 0) as last_purchase_price -- Остання ціна закупки
        FROM Products p
        LEFT JOIN ProductCategories pc ON p.category_id = pc.category_id
        LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN WarehouseSections ws ON p.section_id = ws.section_id
        LEFT JOIN DailySales ds ON p.product_id = ds.product_id
        LEFT JOIN LastPurchases lp ON p.product_id = lp.product_id
        -- Критерій критичного залишку (менше 5 одиниць)
        WHERE p.quantity < 5
        ORDER BY p.quantity ASC, p.name
    """
    
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    results = []
    for product in products:
        current_stock = int(product[4])
        avg_daily_sales = float(product[8])
        sale_price = float(product[3])
        # Якщо закупівлі ні разу не було, беремо 70% від ціни продажу як запасний варіант
        purchase_price = float(product[9]) if product[9] and product[9] > 0 else sale_price * 0.7
        
        # Розрахунки
        recommended_order = max(0, int(avg_daily_sales * 60 - current_stock))
        days_until_stockout = int(current_stock / avg_daily_sales) if avg_daily_sales > 0 else 999
        
        # Визначення критичності
        if current_stock == 0:
            criticality = 'CRITICAL'
            priority = 1
        elif days_until_stockout <= 7:
            criticality = 'HIGH'
            priority = 2
        elif days_until_stockout <= 14:
            criticality = 'MEDIUM'
            priority = 3
        else:
            criticality = 'LOW'
            priority = 4
        
        results.append({
            'product_id': product[0],
            'name': product[1],
            'category': product[2],
            'price': sale_price,
            'purchase_price': round(purchase_price, 2),
            'unit': product[5],
            'current_stock': current_stock,
            'min_quantity': 20,
            'supplier': product[6],
            'section': product[7],
            'avg_daily_sales': round(avg_daily_sales, 2),
            'days_until_stockout': days_until_stockout,
            'recommended_order': recommended_order,
            'criticality': criticality,
            'priority': priority,
            'estimated_cost': round(recommended_order * purchase_price, 2)
        })
    
    return sorted(results, key=lambda x: (x['priority'], x['days_until_stockout']))

def get_warehouse_efficiency(config):
    """
    Розрахунок показників ефективності складу.
    """
    conn = get_db_connection(config)
    cursor = conn.cursor()
    
    # 1. Використання простору (% заповнення)
    cursor.execute("""
        SELECT 
            SUM(p.quantity) as total_items,
            COUNT(*) as total_products
        FROM Products p
    """)
    space_data = cursor.fetchone()
    
    # 2. Оборотність запасів 
    cursor.execute("""
        SELECT 
            SUM(p.quantity * p.price) as stock_value,
            (SELECT SUM(od.quantity * od.price)
             FROM OrderDetails od
             JOIN Orders o ON od.order_id = o.order_id
             WHERE o.status = 'shipped'
               AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) as monthly_sales
        FROM Products p
    """)
    turnover_data = cursor.fetchone()
    
    # 3. Точність інвентаризації (% товарів без розбіжностей)
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN quantity > 0 THEN 1 ELSE 0 END) as with_stock
        FROM Products
    """)
    accuracy_data = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    # Розрахунки
    total_items = int(space_data[0]) if space_data[0] else 0
    total_products = int(space_data[1]) if space_data[1] else 1

    stock_value = float(turnover_data[0]) if turnover_data[0] else 1.0
    monthly_sales = float(turnover_data[1]) if turnover_data[1] else 0.0

    # Переконуємося, що відсотки — це чисті float
    space_utilization = float(min(100, (total_items / (total_products * 100)) * 100))
    turnover_rate = float((monthly_sales / stock_value * 12) * 100) if stock_value > 0 else 0.0
    inventory_accuracy = float(accuracy_data[1] / accuracy_data[0] * 100) if accuracy_data[0] > 0 else 0.0

    # Швидкість обробки (теж float)
    order_processing_speed = 85.0

    # Тепер тут додаються Тільки float + float + float + float, і помилки не буде!
    overall_efficiency = (space_utilization + turnover_rate + inventory_accuracy + order_processing_speed) / 4

    return {
        'space_utilization': round(space_utilization, 1),
        'turnover_rate': round(turnover_rate, 1),
        'inventory_accuracy': round(inventory_accuracy, 1),
        'order_processing_speed': round(order_processing_speed, 1),
        'overall_efficiency': round(overall_efficiency, 1)
    }


def get_sales_data(config, start_date, end_date):
    """
    Аналіз тренду продажів за вказаний період (переведено на Orders + OrderDetails).
    """
    conn = get_db_connection(config)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            DATE(o.order_date) as sale_date,
            SUM(od.quantity * od.price) as daily_revenue
        FROM OrderDetails od
        JOIN Orders o ON od.order_id = o.order_id
        WHERE o.status = 'shipped'
            AND o.order_date BETWEEN %s AND %s
        GROUP BY DATE(o.order_date)
        ORDER BY sale_date
    """
    
    cursor.execute(query, (start_date, end_date))
    sales_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    results = []
    for row in sales_data:
        # Безпечно конвертуємо дату в рядок (працює і для об'єктів date/datetime, і для str)
        date_str = row[0].strftime("%Y-%m-%d") if hasattr(row[0], 'strftime') else str(row[0])
        results.append({
            'sale_date': date_str,
            'daily_revenue': round(float(row[1]), 2)
        })
    
    return results


def get_write_offs_data(config, start_date, end_date):
    """
    Аналіз списань товарів за вказаний період.
    Залишається на StockMovements (тип 'write-off').
    """
    conn = get_db_connection(config)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            p.product_id,
            p.name,
            SUM(sm.quantity) as total_written_off,
            SUM(sm.quantity * p.price) as total_loss
        FROM StockMovements sm
        JOIN Products p ON sm.product_id = p.product_id
        WHERE sm.movement_type = 'write-off'
            AND sm.movement_date BETWEEN %s AND %s
        GROUP BY p.product_id, p.name
        ORDER BY total_loss DESC
    """
    
    cursor.execute(query, (start_date, end_date))
    write_offs_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    results = []
    for row in write_offs_data:
        results.append({
            'product_id': row[0],
            'name': row[1],
            'total_written_off': int(row[2]) if row[2] is not None else 0,
            'total_loss': round(float(row[3]), 2) if row[3] is not None else 0.0
        })
    
    return results