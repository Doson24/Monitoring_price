from dataclasses import dataclass
import time
from datetime import datetime
from logger import init_logger, logger_obj
import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc

from driver import init_webdriver
from save_DB import save_db

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
def setup_city(driver):
    driver.get('https://www.ozon.ru/')
    button_city = driver.find_elements(By.XPATH, './/button[@tabindex="0"]')[2]
    if button_city.text == 'Укажите адрес доставки':
        button_city.click()
        time.sleep(1)
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.XPATH, './/*[@data-widget="commonAddressBook"]/div/div[2]/div/div/div[2]/div[2]'))).click()
        # driver.find_element(By.CLASS_NAME, 'r6d').click()
        time.sleep(1)
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.XPATH, './/input[@type="search"]'))).send_keys('Железногорск')
        # driver.find_element(By.XPATH, './/input[@type="search"]').send_keys('Железногорск')
        time.sleep(1)
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.XPATH,
             './/*[@data-widget="citySelector"]/div[2]/div/div/div'))).click()  # Клик на Железногорск из списка
        # driver.find_elements(By.CLASS_NAME, 'dr0')[0].click()
    else:
        raise Exception('Изменился путь к изменению Адреса доставки')


def monitoring_urls(driver) -> pd.DataFrame:
    with open(r'C:\Users\user\Desktop\Projects\Price_monitoring\Price_item\bat\products.txt', 'r') as f:
        urls = f.readlines()

    setup_city(driver)

    cards = []
    for url in urls:
        driver.get(url)
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(3)

        card = get_one_card_data(driver, url)
        cards.append(card)
        # save_file(asdict(data))
    cards = pd.DataFrame(cards)
    return cards


def get_category_links(driver: uc.Chrome):
    url = 'https://www.ozon.ru/'
    driver.get(url)
    driver.implicitly_wait(30)
    driver.find_element(By.XPATH, './/*[@data-widget="catalogMenu"]/div/button/span').click()
    categories = driver.find_elements(By.XPATH, './/*[@data-widget="catalogMenu"]/div[2]/div/div/ul/li')
    links = []
    for category in categories:
        tag_a = category.find_element(By.TAG_NAME, 'a')
        link = tag_a.get_attribute('href')
        name = tag_a.text
        links.append((name, link))
    return links


def top_products(driver: uc.Chrome):
    links = get_category_links(driver)
    category = {}
    for name, link in links:
        try:
            driver.get(link)
            driver.implicitly_wait(30)

            driver.find_element(By.TAG_NAME, 'aside')

        except:
            continue
        # name = driver.find_element(By.XPATH, './/*[@data-widget="resultsHeader"]/div/h1').text
        sub_categories = driver.find_elements(By.XPATH,
                                              './/aside/div/div/div/div[@style="margin-left:16px;"]/a')

        name_link = [(sub.text, sub.get_attribute('href')) for sub in sub_categories]
        category[name] = name_link
        print(name, name_link)

        get_items_catalog(name_link, driver)


    return category


def get_items_catalog(name_link, driver: uc.Chrome):
    for el in name_link:
        name, link = el
        driver.get(link)
        cards = driver.find_elements(By.XPATH, '//div[contains(@class, "widget-search-result-container")]/div/div')
        data = parse_card(cards)


def parse_card(cards):
    data = []
    for card in cards:
        try:
            name = card.find_element(By.XPATH, './/div[2]/div/a/div').text
        except:
            continue
        link = card.find_element(By.XPATH, './/div/a').get_attribute('href')
        active_price = card.find_element(By.XPATH, './/div[3]/div/div/span').text\
            .encode('ascii', 'ignore').decode("utf-8")
        reviews = card.find_element(By.XPATH, './/div[2]/div/div[2]/div/span[2]').text

        data.append(Card(name, link, active_price, reviews))
    data = pd.DataFrame(data)
    data['reviews']
    return data


if __name__ == '__main__':
    driver = init_webdriver(True)
    # top_products(driver)
    data = monitoring_urls(driver)
    save_db(data,
            path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='Ozon')

    driver.quit()
