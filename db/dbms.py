import os
from typing import Dict, List

import sqlite3


# Подключение к БД.
conn = sqlite3.connect(os.path.join("credits.db"))
cursor = conn.cursor()


def get_cursor():
    return cursor


def delete_db():
    global conn
    global cursor

    os.remove("credits.db")
    conn = sqlite3.connect(os.path.join("credits.db"))
    cursor = conn.cursor()
    _init_db()


def _init_db():
    """
    Создание таблиц в БД (выполняется скрипт 'createdb.sql').
    """
    with open("./db/createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """
    Проверка на наличие таблиц в БД через таблицу 'sqlite_master'.
    В случае отстутсвия создаются.
    """
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='Cost'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
