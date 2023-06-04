from dataclasses import dataclass, asdict
import time
from datetime import datetime
from pprint import pprint

import pandas as pd
from save_DB import save_db
from SqlLite import add_data
from driver import init_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class Card:
    name: str
    link: str
    date_create: str
    active_price: str
    prev_price: str
    catalog: str
    city: str


def select_city(driver):
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'city-select__text_BTU')))
    driver.find_element(By.CLASS_NAME, 'city-select__text_BTU').click()  # Кнопка выбора города
    time.sleep(3)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'city-bubble_IBz')))
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, 'city-bubble_IBz')))
    cities = driver.find_elements(By.CLASS_NAME, 'city-bubble_IBz')  # Выбор Красноярска из списка
    cities[12].click()
    return cities[12].text


def parse_card(driver, city):
    items = driver.find_elements(By.CLASS_NAME, 'catalog-product.ui-button-widget ')
    category = driver.current_url.split('/')[-2]
    if len(items) < 18:
        driver.refresh()
        time.sleep(10)
        items = driver.find_elements(By.CLASS_NAME, 'catalog-product.ui-button-widget ')

    page_data = []
    for item in items:
        name = item.find_element(By.CLASS_NAME, 'catalog-product__name.ui-link.ui-link_black').text
        link = item.find_element(By.CLASS_NAME, 'catalog-product__name.ui-link.ui-link_black').get_attribute('href')
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-buy__price')))
        except:
            driver.refresh()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-buy__price')))
        price = item.find_element(By.CLASS_NAME, 'product-buy__price').text
        price = price.replace('&nbsp;₽', '').replace('₽', '').replace(' ', '')

        date = datetime.today().strftime("%d.%m.%Y")
        if '\n' in price:
            active_price, prev_price = price.split('\n')
        else:
            active_price, prev_price = price, price

        page_data.append(Card(name, link, date, active_price, prev_price, catalog=category, city=city))

    return page_data


def max_number_page(driver):
    time.sleep(5)
    pages = driver.find_elements(By.CLASS_NAME, 'pagination-widget__page')
    number = pages[-1].get_attribute('data-page-number')
    return int(number)


def parse_catalog(driver, city, base_url):
    data_catalog = []
    number = max_number_page(driver)
    print(number, "страниц найдено")
    for page in range(1, number + 1):
        url = f'{base_url}?p={page}'
        driver.get(url)
        driver.implicitly_wait(1)
        try:
            cards_page = parse_card(driver, city)
        except Exception as e:
            cards_page = None
            print(f"[-] {page} page - Ошибка загрузки")

        if cards_page:
            data_catalog.extend(cards_page)

        driver.implicitly_wait(1)
        print(f'[+] {page} page complete, count={len(cards_page)}')
    return data_catalog


def save_file(data, filename='Data.csv'):
    df_data = pd.DataFrame(data)
    df_data.to_csv(filename, mode='a', index=False, header=False)


def main():
    base_urls = [
        'https://www.dns-shop.ru/catalog/17a8a05316404e77/planshety/',
        'https://www.dns-shop.ru/catalog/17a89a3916404e77/operativnaya-pamyat-dimm/',
        'https://www.dns-shop.ru/catalog/17a9b91b16404e77/operativnaya-pamyat-so-dimm/',
        'https://www.dns-shop.ru/catalog/17a9ef1716404e77/naushniki-i-garnitury/',
        'https://www.dns-shop.ru/catalog/17a8a69116404e77/myshi/'
    ]
    selected_city = False
    driver = init_webdriver()

    for base_url in base_urls:
        driver.get(base_url)
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(1)
        if not selected_city:
            try:
                city = select_city(driver)
            except:
                city = 'Ошибка'
            else:
                selected_city = True
            print(city, "г выбран")
        # Parse Category
        data_catalog = parse_catalog(driver, city, base_url)
        data = pd.DataFrame(data_catalog)
        save_db(data)

    driver.quit()


if __name__ == '__main__':
    main()
