import os
import sqlite3
import json
from sqlite3 import Error

from logger.logger_rest_client import logger_rest_client

db_file = "storage/my_database.db"

def check_db():
    return os.path.exists(db_file)

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        logger_rest_client.error(f"Ошибка подключения: {e}")
    return conn

def create_table():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS params (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pf TEXT 
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            conn.close()
            logger_rest_client.info(f"Ошибка создания таблицы: {e}")
            return False
    else:
        logger_rest_client.error("Ошибка подключения к базе данных.")
        return False

def clear_table():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM params')
            conn.commit()
            cursor.execute('VACUUM')
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            conn.close()
            logger_rest_client.error(f"Ошибка при очистки таблицы: {e}")
            return False
    else:
        logger_rest_client.error("Ошибка подключения к базе данных.")
        return False

def select_params(conn, n):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM params LIMIT ?', (n,))
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Exception as e:
        conn.rollback()
        logger_rest_client.error(f"Ошибка извлечения данных: {e}")
        return None

def delete_params(conn, ids_list_delete):
    try:
        cursor = conn.cursor()
        ids_string = ', '.join(str(id) for id in ids_list_delete)
        query = f'DELETE FROM params WHERE id IN ({ids_string})'
        cursor.execute(query)
        count_rows = cursor.rowcount
        conn.commit()
        cursor.close()
        logger_rest_client.info(f"Удалено {count_rows} записей.")
        return count_rows
    except Exception as e:
        conn.rollback()
        logger_rest_client.error(f"Ошибка удаления данных: {e}")

def vacuum_db(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        conn.commit()
        cursor.close()
        logger_rest_client.info("База данных оптимизирована (VACUUM).")
    except Exception as e:
        conn.rollback()
        logger_rest_client.error(f"Ошибка при выполнении VACUUM: {e}")