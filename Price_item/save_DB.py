from pprint import pprint
import pandas as pd
from SqlLite import add_data


def save_db(cards, name_db='online_markets.db', table_name='DNS_CityLink'):
    cards = pd.DataFrame(cards)
    pprint(cards[['name', 'active_price']])
    add_data(cards,
             name_db=name_db,
             table_name=table_name)
    print('>>>Запись в БД завершена<<<')