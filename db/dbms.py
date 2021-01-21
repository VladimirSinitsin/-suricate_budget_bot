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


def table_is_empty(table: str) -> bool:
    """
    Содержит ли таблица строки.
    :param table: название таблицы.
    :return:
    """
    cursor.execute(f"SELECT * FROM {table}")
    return False if cursor.fetchall() else True


def add_cost(cost: Dict) -> None:
    """
    Добавление расхода в таблицу.
    :param cost: словарь с данными по расходу.
    :return:
    """
    insert("Cost", {"data": cost['дата'],
                    "payer": cost['плательщик'],
                    "credit": cost['сумма'],
                    "shop": cost['магазин']})


def add_payer(name: str) -> None:
    """
    Добавление плательщика в таблицу.
    :param name: имя плательщика.
    :return:
    """
    if len(all_payers()) >= 2:
        raise Exception("Достугнуто максимальное количество плательщиков (2)!")
    insert("Payer", {"name": name})


def other_payer(payer: str) -> str:
    """
    Получение имени второго плательщика.
    :param payer: имя данного плательщика.
    :return: имя второго.
    """
    payers = all_payers()
    current_index = payers.index(payer)
    return payers[current_index - 1]


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
    cursor.execute(f'delete from Payer where name="{name}"')
    conn.commit()


def total_credit() -> str:
    """
    Итог, кто сколько должен.
    :return: вывод.
    """
    cursor.execute("SELECT payer, SUM(credit) "
                   "FROM Cost "
                   "GROUP BY payer")
    rows = cursor.fetchall()
    if not rows:
        return "Расходов не было."
    elif len(rows) == 1:
        return f"{other_payer(rows[0][0])} должен(-на) {round(float(rows[0][1]), 2)}"
    elif float(rows[0][1]) == float(rows[1][1]):
        return "Вы в рассчёте"
    elif float(rows[0][1]) > float(rows[1][1]):
        return f"{rows[1][0]} должен(-на) {round(float(rows[0][1]) - float(rows[1][1]), 2)}"
    else:
        return f"{rows[0][0]} должен(-на) {round(float(rows[1][1]) - float(rows[0][1]), 2)}"


def all_costs() -> List:
    cursor.execute("SELECT * "
                   "FROM Cost ")
    rows = cursor.fetchall()
    costs = [f"{row[0]}) {row[1]} {row[2]} совершил(-а) покупку на {row[3]} в {row[4]}" for row in rows]
    return costs


def all_payers() -> List:
    """
    Все плательщики.
    :return: список строк-имён.
    """
    cursor.execute("SELECT * "
                   "FROM Payer ")
    rows = cursor.fetchall()
    names = [row[0] for row in rows]
    return names


def current_payers() -> List:
    """
    Все плательщики, совершавшие покупки.
    :return: список строк-имён.
    """
    cursor.execute("SELECT payer "
                   "FROM Cost "
                   "GROUP BY payer")
    rows = cursor.fetchall()
    names = [row[0] for row in rows]
    return names


def delete_db() -> None:
    """
    Полная очистка БД.
    :return:
    """
    global conn
    global cursor

    os.remove("credits.db")
    conn = sqlite3.connect(os.path.join("credits.db"))
    cursor = conn.cursor()
    _init_db()


def delete_all_costs() -> None:
    """
    Очистка всех расходов из БД.
    :return:
    """
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
    """
    Очистка всех плательщиков из БД.
    :return:
    """
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
