from dataclasses import dataclass, asdict
import time
from datetime import datetime
from logger import init_logger, logger_obj
import pandas as pd
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from driver import init_webdriver
from save_DB import save_db
from threading import Thread
import multiprocessing
from benchmark import benchmark

log = init_logger('ozon')


@dataclass
class Card:
    name: str
    link: str
    active_price: int
    reviews: int
    # sold: int
    # catalog: str
    date_create: str = datetime.today().strftime("%d-%m-%Y")

    def __str__(self):
        return f'{self.name}, {self.link}'


@dataclass
class Card_top:
    name: str
    link: str
    active_price: int
    reviews: int
    # sold: int
    catalog: str
    date_create: str = datetime.today().strftime("%d-%m-%Y")

    def __str__(self):
        return f'{self.name}, {self.link}'


@logger_obj(log)
def get_one_card_data(driver, base_url):
    try:
        name = WebDriverWait(driver, 30). \
            until(EC.presence_of_element_located((
            (By.XPATH, ".//div[@data-widget='webProductHeading']"))))
    except TimeoutException:
        sold_out = driver.find_element(By.XPATH, './/*[@data-widget="webOutOfStock"]/h2').text
        name = driver.find_element(By.XPATH,
                                   './/*[@data-widget="webOutOfStock"]/div/div/div/div/div[2]/p')
        return Card(name.text, base_url, sold_out, sold_out)
    # name = driver.find_element(By.XPATH, ".//*[@data-widget='webProductHeading']").text

    layout = driver.find_elements(By.XPATH, ".//*[@data-widget='webReviewProductScore']")[0].text
    layout = layout.split('\n')
    rewiews = layout[0].split(' ')[0]

    try:
        cost_ozon = driver.find_element(By.XPATH, ".//*[@data-widget='webOzonAccountPrice']").text
    except:
        cost_ozon = driver.find_element(By.XPATH, ".//*[@data-widget='webPrice']").text
    cost_ozon_clen = cost_ozon.replace('\u2009', '').split('₽')[0]

    return Card(name.text, base_url, int(cost_ozon_clen), rewiews)


@logger_obj(log)
def save_file(data):
    path = 'C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\data\\Samura.csv'
    df = pd.DataFrame([data])
    print(df[df.columns[-3:]])
    df.to_csv(path, mode='a', index=False, header=False)
    print('>>>Сохранение завершено<<<')


@logger_obj(log)
def setup_city(driver: uc.Chrome, delivery_city='Железногорск'):
    driver.get('https://www.ozon.ru/')
    driver.implicitly_wait(5)
    try:
        button_city = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, './/div[@data-content]/div[3]/div/button[@tabindex="0"]')))
    except:
        button_city = driver.find_elements(By.XPATH,
            '//*[@data-widget="addressBookBarWeb"]//*[@tabindex="0" and @type="button"]')[1]

    # button_city = button_city[2]
    # button_city = driver.find_elements(By.XPATH, './/button[@tabindex="0"]')[2]
    if button_city.text == 'Укажите адрес доставки' or button_city.text == 'Уточнить адрес':
        time.sleep(3)
        button_city.click()
        # driver.implicitly_wait(3)
        try:
            WebDriverWait(driver, 120).until(EC.presence_of_element_located(
                (By.XPATH, './/*[@data-widget="commonAddressBook"]/div/div[2]/div/div/div[2]/div[2]'))).click()
        except TimeoutException:
            raise 'Ошибка нажатия на кнопку "Укажите адрес доставки"'
        # driver.find_element(By.CLASS_NAME, 'r6d').click()
        time.sleep(1)
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.XPATH, './/input[@type="search"]'))).send_keys(delivery_city)
        # driver.find_element(By.XPATH, './/input[@type="search"]').send_keys('Железногорск')
        time.sleep(1)
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.XPATH,
             './/*[@data-widget="citySelector"]/div[2]/div/div/div'))).click()  # Клик на Железногорск из списка
        # driver.find_elements(By.CLASS_NAME, 'dr0')[0].click()
    else:
        raise Exception('Изменился путь к изменению Адреса доставки')
    print(f'[+] Город доставки выбран: {delivery_city}')


def monitoring_urls(driver) -> pd.DataFrame:
    with open(r'C:\Users\user\Desktop\Projects\Price_monitoring\Price_item\bat\products.txt', 'r') as f:
        urls = f.readlines()

    driver.set_window_size(1920, 1080)
    setup_city(driver)

    cards = []
    for url in urls:
        driver.get(url)
        # driver.implicitly_wait(3)

        card = get_one_card_data(driver, url)
        cards.append(card)
        print(card, end='')
        # save_file(asdict(data))
    cards = pd.DataFrame(cards)
    return cards


def get_category_links(driver: uc.Chrome):
    url = 'https://www.ozon.ru/'
    driver.get(url)
    # driver.implicitly_wait(3)
    catalog_menu = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.XPATH, './/*[@data-widget="catalogMenu"]/div/button/span')))
    catalog_menu.click()
    categories = driver.find_elements(By.XPATH, './/*[@data-widget="catalogMenu"]/div[2]/div/div/ul/li')
    links = []
    for category in categories:
        try:
            tag_a = WebDriverWait(category, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        except TimeoutException:
            driver.refresh()
            tag_a = WebDriverWait(category, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        # tag_a = category.find_element(By.TAG_NAME, 'a')
        link = tag_a.get_attribute('href')
        name = tag_a.text
        links.append((name, link))
    return links


@benchmark
def top_products(driver: uc.Chrome):
    # setup_city(driver)
    links_category = get_category_links(driver)
    category = {}
    # data = []
    for name, link in links_category[:]:
        try:
            driver.get(link)
            print('-' * 5, name, link)
            # driver.implicitly_wait(30)

            driver.find_element(By.TAG_NAME, 'aside')
        except:
            print(f'[-] Error open Category {name} - {link}')
            continue
        # name = driver.find_element(By.XPATH, './/*[@data-widget="resultsHeader"]/div/h1').text
        sub_categories = driver.find_elements(By.XPATH,
                                              './/aside/div/div/div/div[@style="margin-left:16px;"]/a')

        names_links = [(sub.text, sub.get_attribute('href')) for sub in sub_categories]
        category[name] = names_links

        names_links = get_subsub_categories_links(names_links, driver)
        items_catalog = get_items_catalog(names_links, driver)
        # data.extend(items_catalog)

        data = pd.DataFrame(items_catalog)
        save_db(data,
                path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
                table_name='Ozon_top')
        print(name, names_links)

    # return data


@benchmark
def get_subsub_categories_links(names_links: list, driver: uc.Chrome):
    data = []
    for el in names_links:
        name, link = el
        driver.get(link)
        hrefs = driver.find_elements(By.XPATH, '//div[@style="margin-left:16px;"]/a')
        links = [href.get_attribute('href') for href in hrefs]
        data.append((name, links))
    print('[+]Func get_subsub_categories_links')
    return data


@benchmark
def get_items_catalog(names_links: list, driver: uc.Chrome) -> list:
    data = []
    for el in names_links:
        name, links = el
        for link in links:
            driver.get(link + '?brandcertified=t')
            scroll_page(driver)
            try:
                cards = search_cards(driver)
            except TimeoutException:
                print(f'[Error]Func get_items_catalog TimeoutException: {link}')
                continue
            cards = parse_cards(cards, name, driver)

            data.extend(cards)
        print(f'[+] SubCategory {name} parse is complete')
    return data


@benchmark
def search_cards(driver, wait=10):
    driver.implicitly_wait(1)
    return WebDriverWait(driver, wait).until(
        EC.presence_of_all_elements_located((
            By.XPATH, '//div[contains(@class, "widget-search-result-container")]/div/div')))


@benchmark
def parse_cards(cards: list, category, driver, wait=0.3) -> list[Card_top]:
    data = []
    tag_view = 3
    for i, card in enumerate(cards):
        try:
            name = search_name(card)
        except:
            try:
                cards = search_cards(driver)
                card = cards[i]
            except (IndexError, TimeoutException):
                continue
            try:
                name = search_name(card)
            except:
                driver.refresh()
                scroll_page(driver)
                cards = search_cards(driver)
                print(f'[-] Cannot find name')
                continue
        link = WebDriverWait(card, wait).until(EC.presence_of_element_located((By.XPATH, './/div/a'))) \
            .get_attribute('href')
        try:
            active_price = WebDriverWait(card, wait).until(
                EC.presence_of_element_located((By.XPATH, f'.//div[{tag_view}]/div/div/span'))) \
                .text \
                .encode('ascii', 'ignore').decode("utf-8")
            if active_price == '':
                raise NoSuchElementException
        except (TimeoutException, NoSuchElementException):
            try:
                tag_view = 1
                active_price = WebDriverWait(card, 1).until(
                    EC.presence_of_element_located((By.XPATH, f'.//div[{tag_view}]/div/div/span'))) \
                    .text \
                    .encode('ascii', 'ignore').decode("utf-8")
                if active_price == '':
                    raise NoSuchElementException
            except (TimeoutException, NoSuchElementException):
                print(f'[-] Cannot find price {name}, {link}')
                continue
        start = time.time()
        try:
            reviews = WebDriverWait(driver, wait).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(@class, " tsBodyMBold")]/span[2]')))
            reviews = reviews.text
        except TimeoutException:
            print(f'[-] Cannot find reviews {name}, {link}')
            end = time.time()
            print('[*]', end - start, 'Время поиска Reviews')
            continue
        card_top = Card_top(name, link, active_price, reviews, category)
        print(i, card_top)
        data.append(card_top)
    return data


def scroll_page(driver):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)


# //div[@class="c7" and @data-widget="column"]
def break_process(delay):
    time.sleep(delay)
    raise TimeoutException


def search_name(card):
    # driver.implicitly_wait(1)
    # time.sleep(1)
    name = WebDriverWait(card, 0.5).until(
        EC.presence_of_element_located(
            (By.XPATH, './/a[contains(@class, "tile-hover-target ")]'))).text
    return name


if __name__ == '__main__':
    start = datetime.now()
    driver = init_webdriver(False)
    data = monitoring_urls(driver)
    save_db(data,
            path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='Ozon')
    print('Время выполнения: ', datetime.now() - start)
    driver.close()
