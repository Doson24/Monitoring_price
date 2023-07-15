from datetime import datetime

from dataclasses import dataclass, asdict

import pandas as pd
from driver import init_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from save_DB import save_db


@dataclass
class Card:
    name: str
    active_price: str
    no_discount: str
    discount: str
    rating: str
    reviews: str
    link: str
    date_create: str = datetime.today().strftime("%d/%m/%Y")


class Config:
    def __init__(self, headless=False):
        self.driver = init_webdriver(headless)

    def config_driver(self):
        self.driver.set_window_size(1920, 1080)
        self.driver.implicitly_wait(1)


class Catalog_items(Config):
    """
    Парсинг каталога
    """

    def __init__(self, url, headless=True):
        super().__init__(headless)
        self.url = url
        self.cards = []

    def get_items_page(self, param):
        self.driver.get(self.url + param)
        self.config_driver()

        items = self.driver.find_elements(By.CLASS_NAME, 'catalog-card.catalog-card--new')
        for item in items:
            url_card = item.find_element(By.XPATH, './/a[@data-const="product_link"]').get_attribute('href')
            text = item.find_element(By.CLASS_NAME, 'catalog-card__price').text
            discount = text.split('\n')[0]
            active_price = text.split('\n')[1]
            no_discount = text.split('\n')[2]
            name = item.find_element(By.CLASS_NAME, 'catalog-card__title').text
            rate = item.find_element(By.CLASS_NAME, 'rating')
            rating = rate.get_attribute('data-test-listing-rating')
            reviews = rate.get_attribute('data-test-listing-reviews')

            self.cards.append(Card(name, active_price, no_discount, discount, rating, reviews, url_card))
        print(f'[+] {len(items)} cards added')
        return self.cards

    @property
    def find_count_pages(self):
        self.driver.get(self.url)
        elemets = self.driver.find_elements(By.XPATH, '//*[contains(@class, "pagination-btn")]')
        return len(elemets)


class Card_ascona(Config):
    """
    Парсинг данных на прямую по ссылке на карточку матраса
    """
    def __init__(self, url_card, headless=True):
        super().__init__(headless)
        self.date = None
        self.name = None
        self.url_card = url_card
        self.no_discount = None
        self.discount = None
        self.active_price = None

        self.get_data()
        self.data_card = self.to_df()

    def get_data(self):
        self.driver.get(self.url_card)
        self.config_driver()

        price = self.driver.find_element(By.XPATH, '//*[@data-test-card-new-price]').text
        self.discount = price
        self.no_discount = self.driver.find_element(By.XPATH, '//*[@data-test-card-old-price]').text

        el_name = self.driver.find_element(By.XPATH, '//*[@data-test-card-name]')
        self.name = el_name.get_attribute('data-test-card-name')
        # feedback = get_name[1]

        self.date = datetime.today().strftime('%Y-%m-%dT%H:%M')

    def to_df(self):
        data = pd.DataFrame([{
            'name': self.name,
            'discount': self.discount,
            'no discount': self.no_discount,
            # 'feedback': feedback,
            'url': self.url_card,
            'create_date': self.date
        }])
        return data


if __name__ == '__main__':
    # url_card = 'https://krasnoyarsk.askona.ru/matrasy/astoria.htm/?SELECTED_HASH_SIZE=160x200-af13bfd624e1acd34f2103481efea402&SELECTED_FABRIC_ID=0'
    url_catalog = 'https://krasnoyarsk.askona.ru/matrasy/'
    param = '?page='

    # ascona_card = Card_ascona(url_card, headless=False)
    # data = ascona_card.data_card
    # print(data)

    ascona = Catalog_items(url_catalog, True)
    pages = ascona.find_count_pages

    for num in range(1, pages):
        print(f'Page {num}')
        ascona.get_items_page(param + str(num))
    data = pd.DataFrame(ascona.cards)

    # print('>>>Сохранение<<<')
    # path = 'C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\data\\askona.csv'
    # data.to_csv(path, mode='a', index=False, header=False)

    save_db(data,
            path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='Ascona')