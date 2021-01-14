import os
from typing import Dict, List

import sqlite3


# Подключение к БД.
conn = sqlite3.connect(os.path.join("credits.db"))
cursor = conn.cursor()


def get_cursor():
    return cursor


def insert(table: str, column_values: Dict) -> None:
    """
    Метод реализующий INSERT для БД.
    :param table: название таблицы.
    :param column_values: столбцы для вставки и значения.
    """
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Dict]:
    """
    Все записи из конкретных столбцов таблицы.
    :param table: название таблицы.
    :param columns: список нужных столбцов.
    :return: список словарей-строк, в котором ключ - название столбца.
    """
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete_cost(row_id: int) -> None:
    """
    Удаление долга из БД по id.
    """
    row_id = int(row_id)
    cursor.execute(f"delete from Cost where id={row_id}")
    conn.commit()


def delete_payer(name: str) -> None:
    """
    Удаление плательщика из БД.
    """
    cursor.execute(f"delete from Payer where name={name}")
    conn.commit()


def all_credits() -> List:
    cursor.execute("SELECT payer, SUM(credit) "
                   "FROM Cost "
                   "GROUP BY payer")
    rows = cursor.fetchall()
    return rows


def all_payers() -> List:
    cursor.execute("SELECT * "
                   "FROM Payer ")
    rows = cursor.fetchall()
    names = [row[0] for row in rows]
    return names


def delete_db() -> None:
    global conn
    global cursor

    os.remove("credits.db")
    conn = sqlite3.connect(os.path.join("credits.db"))
    cursor = conn.cursor()
    _init_db()


def delete_all_costs() -> None:
    cursor.execute(f"DROP TABLE Cost;")
    cursor.execute("CREATE TABLE Cost("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "data DATATIME,"
                   "payer TEXT,"
                   "credit DECIMAL,"
                   "shop TEXT"
                   ");")
    conn.commit()


def delete_all_payers() -> None:
    cursor.execute(f"DROP TABLE Payer;")
    cursor.execute("CREATE TABLE Payer("
                   "name TEXT PRIMARY KEY"
                   ");")
    conn.commit()


def _init_db() -> None:
    """
    Создание таблиц в БД (выполняется скрипт 'createdb.sql').
    """
    with open("./db/createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists() -> None:
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
