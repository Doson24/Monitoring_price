from dataclasses import dataclass, asdict
import time
from datetime import datetime
from pprint import pprint
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from save_DB import save_db
# from SqlLite import add_data
from driver import init_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


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
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'elgmz660.e106ikdt0.css-1r38efs.e1gjr6xo0')))
    driver.find_element(By.CLASS_NAME, 'elgmz660.e106ikdt0.css-1r38efs.e1gjr6xo0').click()  # Кнопка выбора города
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.NAME, 'search-city')))
    input = driver.find_element(By.NAME, 'search-city')  # Выбор Красноярска из списка
    input.send_keys('Красноярск')
    driver.find_element(By.CLASS_NAME, 'css-sl5paq.ek3bndn0').click()


def parse_card(driver, city) -> list:
    items = WebDriverWait(driver, 60).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, 'e12wdlvo0.app-catalog-1bogmvw.e1loosed0 ')))
    # if len(items) < 48:
    #     driver.refresh()
    #     items = WebDriverWait(driver, 30).until(
    #         EC.presence_of_all_elements_located((By.CLASS_NAME, 'e12wdlvo0.app-catalog-1bogmvw.e1loosed0 ')))

    category = driver.current_url.split('/')[-2]
    names = WebDriverWait(driver, 60).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, 'app-catalog-1tp0ino.e1an64qs0')))
    links = WebDriverWait(driver, 60).until(
        EC.visibility_of_all_elements_located((By.XPATH, '//*[@class="app-catalog-1tp0ino e1an64qs0"]/a')))
    # driver.implicitly_wait(3)
    page_data = []

    for item in items:
        try:
            name = item.find_element(By.CLASS_NAME, 'app-catalog-1tp0ino.e1an64qs0')
            name = name.text
            link = item.find_element(By.XPATH, './/*[@class="app-catalog-1tp0ino e1an64qs0"]/a')
            link = link.get_attribute('href')
            try:
                price = WebDriverWait(item, 3).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, 'e1j9birj0.e106ikdt0.app-catalog-j8h82j.e1gjr6xo0'))).text
            except:
                price = 'Нет товара'
            date = datetime.today().strftime("%d-%m-%Y")
            active_price, prev_price = price, price
        except:
            print("Ошибка чтения товара")
        else:
            page_data.append(Card(name, link, date, active_price, prev_price, catalog=category, city=city))
        # print(name)
    return page_data


def max_number_page(driver):
    time.sleep(5)
    pages = driver.find_elements(By.CLASS_NAME, 'app-catalog-h5nagc.ero1s990')
    number = pages[-1].text
    return int(number)


def parse_catalog(driver, city, base_url):
    data_catalog = []
    number = max_number_page(driver)
    print(number, "страниц найдено")

    for page in range(1, number + 1):
        url = f'{base_url}?p={page}&view_type=list'
        driver.get(url)
        driver.implicitly_wait(3)

        try:
            try:
                try:
                    cards_page = parse_card(driver, city)
                except Exception as st:
                    print(st)
                    cards_page = parse_card(driver, city)
            except Exception as st:
                print(st)
                cards_page = parse_card(driver, city)
        except TimeoutException as t:
            print(t.stacktrace)
            driver.refresh()
            print('[?] Refresh driver')
            cards_page = parse_card(driver, city)
        if cards_page:
            data_catalog.extend(cards_page)

        driver.implicitly_wait(3)
        print(f'[+] {page} page complete, count={len(cards_page)}')
    print(data_catalog[0].catalog)
    return data_catalog


def save_file(data):
    df_data = pd.DataFrame(data)
    df_data.to_csv('Data.csv', mode='a', index=False, header=False)


def get_items_catalog(driver, base_urls, table_name):
    selected_city = False

    for base_url in base_urls:
        driver.get(base_url + '?view_type=list')
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(3)

        if not selected_city:
            try:
                select_city(driver)
            except:
                city = 'Ошибка'
            else:
                selected_city = True
                city = 'Красноярск'
                print(city, "г выбран")
        # Parse Category
        try:
            data_catalog = parse_catalog(driver, city, base_url)
        except:
            print(f'[-] Ошибка {base_url} ')
            continue

        data = pd.DataFrame(data_catalog)
        save_db(data,
                table_name=table_name,
                path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db', )

    driver.quit()


if __name__ == '__main__':
    driver = init_webdriver(True)
    base_urls = [
        "https://www.citilink.ru/catalog/planshety/",
        "https://www.citilink.ru/catalog/myshi/",
        'https://www.citilink.ru/catalog/naushniki',
        'https://www.citilink.ru/catalog/moduli-pamyati/',
        'https://www.citilink.ru/catalog/roboty-pylesosy/',
        'https://www.citilink.ru/catalog/smartfony/',
    ]
    save_table = 'DNS_CityLink'
    get_items_catalog(driver, base_urls, save_table)
