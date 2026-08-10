import pymysql
# Функція для підключення до бази даних
def get_db_connection(config):
    print(f"Підключення до бази даних з конфігурацією: {config}")
    return pymysql.connect(**config)


 