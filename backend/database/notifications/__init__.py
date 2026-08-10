from database.notifications.products import check_low_stock_products, check_expired_products
from database.notifications.orders import check_unprocessed_orders, check_empty_orders
from database.notifications.order_status import check_stale_orders

def gather_all_notifications(config, role: str):
    notifications = []

    if role == "admin":
        notifications.extend(check_low_stock_products(config))
        notifications.extend(check_expired_products(config))
        notifications.extend(check_unprocessed_orders(config))
        notifications.extend(check_empty_orders(config))
        notifications.extend(check_stale_orders(config))
        # Можна додати інші перевірки, які потрібні тільки адміну

    elif role == "manager":
        notifications.extend(check_low_stock_products(config))
        notifications.extend(check_expired_products(config))
        notifications.extend(check_unprocessed_orders(config))
        notifications.extend(check_empty_orders(config))
        notifications.extend(check_stale_orders(config))
        # Менеджер не бачить "застарілі" замовлення, наприклад

    elif role == "employee":
        #notifications.extend(check_low_stock_products(config))
        notifications.extend(check_expired_products(config))
        # Працівник бачить лише сповіщення про склад

    else:
        # Для інших ролей можна повертати порожній список або викликати базові перевірки
        pass

    return notifications
