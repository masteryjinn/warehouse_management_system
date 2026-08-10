import pymysql
from database.utils.connection_manager import get_db_connection

def add_supplier_to_db(config, name, supplier_type, contacts: dict):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT supplier_id FROM Suppliers WHERE name = %s", (name,))
        existing_supplier = cursor.fetchone()

        if existing_supplier:
            print(f"Постачальник '{name}' вже існує (id={existing_supplier[0]})")
            return None 
        # Додаємо клієнта до таблиці suppliers
        cursor.execute("INSERT INTO suppliers (name, type) VALUES (%s, %s)", (name, supplier_type))
        supplier_id = cursor.lastrowid  # Отримуємо ID нового клієнта

        # Додаємо контакти для клієнта
        for contact_type, contact_value in contacts.items():
            if contact_value:
                cursor.execute("""
                    INSERT INTO Contacts_suppliers (supplier_id, contact_type, contact_value)
                    VALUES (%s, %s, %s)
                """, (supplier_id, contact_type, contact_value))

        connection.commit()
        return supplier_id  # Повертаємо ID нового клієнта
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()

def update_supplier_function(config, supplier_id, name, supplier_type, contacts: dict):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Оновлюємо дані постачальника
        print(f"Updating supplier {supplier_id}: name={name}, type={supplier_type}")
        cursor.execute("UPDATE suppliers SET name=%s, type=%s WHERE supplier_id=%s", (name, supplier_type, supplier_id))

        # Оновлюємо або додаємо контакти
        for contact_type, contact_value in contacts.items():
            if contact_value:
                print(f"Updating contact for {contact_type}: {contact_value}")
                
                # Спочатку перевіряємо наявність контакту
                cursor.execute("""
                    SELECT 1 FROM Contacts_suppliers
                    WHERE supplier_id = %s AND contact_type = %s
                """, (supplier_id, contact_type))

                # Якщо запис є (є хоча б один рядок), оновлюємо
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE Contacts_suppliers
                        SET contact_value = %s
                        WHERE supplier_id = %s AND contact_type = %s
                    """, (contact_value, supplier_id, contact_type))
                else:
                    # Якщо запису нема, додаємо новий
                    cursor.execute("""
                        INSERT INTO Contacts_suppliers (supplier_id, contact_type, contact_value)
                        VALUES (%s, %s, %s)
                    """, (supplier_id, contact_type, contact_value))

        connection.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def delete_supplier_from_db(config, supplier_id):
    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        # Видаляємо клієнта з таблиці suppliers
        cursor.execute("DELETE FROM suppliers WHERE supplier_id=%s", (supplier_id,))
        connection.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

def get_suppliers_function(config, page, limit, search=None, name_filter=None, type_filter=None,
                           email_required=None, phone_required=None, address_required=None):
    offset = (page - 1) * limit

    base_query = """
        SELECT 
            c.supplier_id, 
            c.name, 
            c.type,
            MAX(CASE WHEN co.contact_type = 'email' THEN co.contact_value END) AS email,
            MAX(CASE WHEN co.contact_type = 'phone' THEN co.contact_value END) AS phone,
            MAX(CASE WHEN co.contact_type = 'address' THEN co.contact_value END) AS address
        FROM Suppliers c
        LEFT JOIN Contacts_suppliers co ON c.supplier_id = co.supplier_id
    """

    where_clauses = []
    having_clauses = []
    where_params = []
    having_params = []

    if name_filter:
        where_clauses.append("c.name LIKE %s")
        where_params.append(f"%{name_filter}%")

    if type_filter:
        where_clauses.append("c.type = %s")
        where_params.append(type_filter)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += " GROUP BY c.supplier_id"

    if search:
        having_clauses.append("("
            "c.name LIKE %s OR "
            "c.type LIKE %s OR "
            "MAX(CASE WHEN co.contact_type = 'email' THEN co.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN co.contact_type = 'phone' THEN co.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN co.contact_type = 'address' THEN co.contact_value END) LIKE %s"
            ")")
        search_param = f"%{search}%"
        having_params.extend([search_param] * 5)

    if email_required is not None:
        having_clauses.append(
            "MAX(CASE WHEN co.contact_type = 'email' THEN co.contact_value END) IS " +
            ("NOT NULL" if email_required else "NULL")
        )

    if phone_required is not None:
        having_clauses.append(
            "MAX(CASE WHEN co.contact_type = 'phone' THEN co.contact_value END) IS " +
            ("NOT NULL" if phone_required else "NULL")
        )

    if address_required is not None:
        having_clauses.append(
            "MAX(CASE WHEN co.contact_type = 'address' THEN co.contact_value END) IS " +
            ("NOT NULL" if address_required else "NULL")
        )

    if having_clauses:
        base_query += " HAVING " + " AND ".join(having_clauses)

    base_query += " ORDER BY c.supplier_id LIMIT %s OFFSET %s"

    # Обов’язково дотримуйся правильного порядку: WHERE -> HAVING -> LIMIT
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

def count_total_suppliers(config, search=None, name_filter=None, type_filter=None, email_required=None, phone_required=None, address_required=None):
    subquery = """
        SELECT 
            c.supplier_id, 
            c.name, 
            c.type,
            MAX(CASE WHEN co.contact_type = 'email' THEN co.contact_value END) AS email,
            MAX(CASE WHEN co.contact_type = 'phone' THEN co.contact_value END) AS phone,
            MAX(CASE WHEN co.contact_type = 'address' THEN co.contact_value END) AS address
        FROM Suppliers c
        LEFT JOIN Contacts_suppliers co ON c.supplier_id = co.supplier_id
    """

    conditions = []
    params = []
    having_params = []
    having_clauses = []

    if search:
        like_value = f"%{search}%"
        having_clauses.append("("
            "c.name LIKE %s OR "
            "c.type LIKE %s OR "
            "MAX(CASE WHEN co.contact_type = 'email' THEN co.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN co.contact_type = 'phone' THEN co.contact_value END) LIKE %s OR "
            "MAX(CASE WHEN co.contact_type = 'address' THEN co.contact_value END) LIKE %s"
            ")")
        having_params.extend([like_value, like_value, like_value, like_value, like_value])

    if name_filter:
        conditions.append("c.name LIKE %s")
        like_value = f"%{name_filter}%"
        params.append(like_value)

    if type_filter:
        conditions.append("c.type = %s")
        params.append(type_filter)

    if conditions:
        subquery += " WHERE " + " AND ".join(conditions)

    subquery += " GROUP BY c.supplier_id"

    if having_clauses:
        subquery += " HAVING " + " AND ".join(having_clauses)

    full_query = f"""
        SELECT COUNT(*) AS total FROM (
            {subquery}
        ) AS sub
        WHERE 1=1
    """

    # Після агрегації – фільтруємо по email/phone/address
    if email_required is not None:
        if email_required:
            full_query += " AND email IS NOT NULL"
        else:
            full_query += " AND email IS NULL"

    if phone_required is not None:
        if phone_required:
            full_query += " AND phone IS NOT NULL"
        else:
            full_query += " AND phone IS NULL"

    if address_required is not None:
        if address_required:
            full_query += " AND address IS NOT NULL"
        else:
            full_query += " AND address IS NULL"

    connection = get_db_connection(config)
    cursor = connection.cursor()

    try:
        cursor.execute(full_query, params + having_params)
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        connection.close()

def get_suppliers_full(config):
    connection = get_db_connection(config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(query = """
            SELECT 
                s.supplier_id, 
                s.name, 
                s.type,
                MAX(CASE WHEN cs.contact_type = 'email' THEN cs.contact_value END) AS email,
                MAX(CASE WHEN cs.contact_type = 'phone' THEN cs.contact_value END) AS phone,
                MAX(CASE WHEN cs.contact_type = 'address' THEN cs.contact_value END) AS address
            FROM Suppliers s
            LEFT JOIN Contacts_suppliers cs ON s.supplier_id = cs.supplier_id
            WHERE EXISTS (
                SELECT 1 FROM Contacts_suppliers cs 
                WHERE cs.supplier_id = s.supplier_id
            )
            GROUP BY s.supplier_id, s.name, s.type
        """)
        return cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"Помилка MySQL: {err}")
        return []
    finally:
        cursor.close()
        connection.close()