import os
import sqlite3
import json
from sqlite3 import Error

from logger.logger_monitoring import logger_monitoring

db_file = "storage/my_database.db"

def check_db():
    return os.path.exists(db_file)

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        logger_monitoring.error(f"Ошибка подключения: {e}")
    return conn

def insert_params(conn, json_array):
    try:
        cursor = conn.cursor()
        json_data = [(json.dumps(json_obj),) for json_obj in json_array]
        cursor.executemany('INSERT INTO params (pf) VALUES (?)', json_data)
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        conn.rollback()
        logger_monitoring.error(f"Ошибка вставки данных: {e}")
        return False
