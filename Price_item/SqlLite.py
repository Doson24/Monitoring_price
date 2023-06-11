import pandas as pd
import sqlite3


def add_data(df: pd.DataFrame, name_db, table_name):
    # Создание соединения с базой данных SQLite
    conn = sqlite3.connect(name_db)

    # Создание и добавление таблицы в базе данных
    # replace - удалить и вставить, append - добавить
    df.to_sql(table_name, conn, if_exists='append', index=False)
    print("Added in Database")

    # Закрытие соединения с базой данных
    conn.close()
    print("Connection closed")


def create_table(conn: sqlite3.Connection):
    # Создание таблицы в базе данных SQLite
    cur = conn.cursor()
    cur.execute("CREATE TABLE table_name (col1 TEXT, col2 INTEGER, col3 REAL)")


def select_All(name_db, table_name):
    conn = sqlite3.connect(name_db)
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    conn.close()
    return rows
    # for row in rows:
    #     print(row)


if __name__ == "__main__":
    path = 'C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\online_markets.db'
    # data = select_All(path, 'AliExpress')
    # print(data)
    add_data(pd.DataFrame({'data': [1,2,3]}),
             path, 'DNS')