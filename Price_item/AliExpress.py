from dataclasses import dataclass, asdict
import time
from datetime import datetime
from pprint import pprint

import pandas as pd
from driver import init_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from SqlLite import SQLite_operations


@dataclass
class Card:
    name: str
    link: str
    price: str
    reviews: str
    sold: str
    date_create: str
    # catalog: str


def parse_card(driver, city):
    pass


def get_date():
    date = datetime.today().strftime("%d-%m-%Y")
    return date


def parse_catalog(driver, seach_text):
    cards = get_cards(driver)
    last_sold = cards[-1].find_element(By.CLASS_NAME, 'product-snippet_ProductSnippet__sold__lido9p').text
    last_sold = int(last_sold.split(' ')[0])

    while last_sold > 1000:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'snow-ali-kit_Button-Secondary__button'
                                                           '__4468ot.snow-ali-kit_Button__button__1yq34d.snow-ali-kit_Button__sizeM__1yq34d'
                                                           '.SnowSearchProductFeed_SnowSearchProductFeed__moreButton__1tx3x')))
        show_more = driver.find_element(By.CLASS_NAME, 'snow-ali-kit_Button-Secondary__button__4468ot.snow-ali'
                                                       '-kit_Button__button__1yq34d.snow-ali-kit_Button__sizeM__1yq34d'
                                                       '.SnowSearchProductFeed_SnowSearchProductFeed__moreButton__1tx3x')
        show_more.send_keys(Keys.ENTER)

        cards = get_cards(driver)
        last_sold = cards[-1].find_element(By.CLASS_NAME, 'product-snippet_ProductSnippet__sold__lido9p').text
        last_sold = int(last_sold.split(' ')[0])

    date = datetime.today().strftime("%d-%m-%Y")
    items = []
    for card in cards:
        name = card.find_element(By.CLASS_NAME, 'product-snippet_ProductSnippet__name__lido9p').text
        link = card.find_element(By.CLASS_NAME, 'product-snippet_ProductSnippet__description__lido9p').children('a')[
            0].get_attribute('href')
        price = card.find_element(By.CLASS_NAME, 'snow-price_SnowPrice__mainM__18x8np').text
        rate = card.find_element(By.CLASS_NAME, 'product-snippet_ProductSnippet__score__lido9p').text
        sold = card.find_element(By.CLASS_NAME, 'product-snippet_ProductSnippet__sold__lido9p').text
        # Очистка данных
        sold = int(sold.split(' ')[0])

        items.append(Card(name, link, price, rate, sold, seach_text, date))

    return items


def get_cards(driver):
    product_snippet = driver.find_element(By.CLASS_NAME,
                                          'product-snippet_ProductSnippet__grid__lido9p.product'
                                          '-snippet_ProductSnippet__vertical__lido9p'
                                          '.SnowSearchProductFeed_List__grid__vmkcs')
    cards = product_snippet.children('div')
    return cards


def save_file(data, filename):
    df = pd.DataFrame([data])
    print(data)
    df.to_csv(f'data\\{filename}', mode='a', index=False, header=False)
    print('>>>Сохранение<<<')


def get_catalog(driver):
    seach_text = 'Планшеты'

    base_urls = [
        f'https://aliexpress.ru/wholesale?SearchText={seach_text}&SortType=total_tranpro_desc&g=y&page=1',
    ]
    for base_url in base_urls:
        driver.get(base_url)
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(1)

        """try:
            city = select_city(driver)
        except:
            city = 'Ошибка'
        print(city, "г выбран")"""

        # Parse Category
        data_catalog = parse_catalog(driver, seach_text)

        save_file(data_catalog)
    driver.quit()


def get_one_page(driver, file_name, url):
    # url = 'https://aliexpress.ru/item/1005005056409213.html' \
    #       '?sku_id=12000031474584742'
    driver.get(url)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(1)

    name = WebDriverWait(driver, 30) \
        .until(EC.presence_of_element_located((By.CLASS_NAME,
                                               'SnowProductDescription_SnowProductDescription__productName__18hha'))).text
    # name = driver.find_element(By.CLASS_NAME, 'SnowProductDescription_SnowProductDescription__productName__18hha')
    price = driver.find_element(By.CLASS_NAME, 'snow-price_SnowPrice__mainS__azqpin').text
    date_create = get_date()
    reviews = driver.find_element(By.XPATH, '//*[@data-spm="title_floor"]/div/a[2]/span').text
    clear_review = reviews.split(' ')[0].replace('(', '')
    sold = driver.find_element(By.XPATH, '//*[@data-spm="title_floor"]/div/span[2]').text
    clear_sold = sold.split(' ')[0]

    data = Card(name, url, price, clear_review, clear_sold, date_create)
    print(data)
    # save_file(asdict(data), filename=f'{file_name}.csv')
    return data


if __name__ == '__main__':
    driver = init_webdriver(headless=True)

    # get_catalog(driver)
    shopping = {
        'IPAD': 'https://aliexpress.ru/item/1005005056409213.html',
        'Подставка': 'https://aliexpress.ru/item/1005003840912560.html',
        "Стилус": 'https://aliexpress.ru/item/4000426521336.html?sku_id=10000005553945755',
        "Хаб": 'https://aliexpress.ru/item/32863704575.html',
        "Ботинки": 'https://aliexpress.ru/item/4000544117112.html'
    }
    cards = []
    for name, url in shopping.items():
        try:
            card = get_one_page(driver, name, url)
            print(f'[+] Данные {name} загружены')
            cards.append(card)
        except:
            # card = Card(name, url, '', '', '', '')
            card = None
            print(f'[+] Данные {name} не найдены')

    # Запись в БД
    if cards:
        ali = SQLite_operations(db='online_markets.db',
                                table_name='AliExpress')
        cards = pd.DataFrame(cards)
        pprint(cards[['name', 'price']])
        ali.add_data(cards)

    driver.quit()
