from pprint import pprint
import pandas as pd
from SqlLite import SQLite_operations


def save_db(cards: pd.DataFrame,
            path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='DNS_CityLink'):

    db = SQLite_operations(path, table_name)
    cards = pd.DataFrame(cards)
    pprint(cards[['name', 'active_price']])
    db.add_data(cards)
    print('>>>Запись в БД завершена<<<')
