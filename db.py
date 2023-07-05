import psycopg2

from config import *


# Подключение к Базе Данных
def connect_to_database():
    return psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=db_name,
        port=port
    )


# Создание таблицы seen_users
def create_table_seen_users(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS seen_users
                    (
                    id serial PRIMARY KEY,
                    vk_id varchar(20) UNIQUE
                    );'''
                   )
    connection.commit()
    cursor.close()
    print("(SQL) Таблица seen_users = ok")


# Проверка наличия в таблицы seen_users
def check_seen_user(connection, vk_id):
    cursor = connection.cursor()
    cursor.execute('SELECT vk_id FROM seen_users WHERE vk_id=%s;', (vk_id,))
    result = cursor.fetchone()
    cursor.close()
    return result


# Добавление данных в таблицу seen_users
def insert_data_seen_users(connection, vk_id, offset):
    cursor = connection.cursor()

    # cursor = connection.cursor()

    # Проверяем, существует ли запись с таким же vk_id
    cursor.execute('SELECT vk_id FROM seen_users WHERE vk_id = %s;', (vk_id,))
    existing_row = cursor.fetchone()

    # Если запись с таким vk_id уже существует, пропускаем вставку
    if existing_row:
        return

    # Вставляем новую запись с vk_id
    cursor.execute('INSERT INTO seen_users (vk_id) VALUES (%s);', (vk_id,))

    connection.commit()
    cursor.close()
    print(f"(SQL) Запись seen user: {vk_id}")


# Удаление таблицы seen_users. Трай... нужен, чтоб не было ошибки
# при удалении удалённой базы
def remove_table_seen_users(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS seen_users;')
        cursor.execute(
            'CREATE TABLE seen_users (vk_id VARCHAR(255) PRIMARY KEY);')
        connection.commit()
        print("(SQL) Таблица seen_users создана")
    except Exception as e:
        connection.rollback()
        print("(SQL) Ошибка при создании таблицы seen_users:", e)
    finally:
        cursor.close()


# Отключение от Базы Данных
def disconnect_from_database(connection):
    connection.close()


if __name__ == "__main__":
    connection = connect_to_database()
    create_table_seen_users(connection)

    vk_id = "check"
    offset = 0
    insert_data_seen_users(connection, vk_id, offset)
    print(check_seen_user(connection, vk_id))
    disconnect_from_database(connection)
