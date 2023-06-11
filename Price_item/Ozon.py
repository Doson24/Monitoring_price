import csv
from dataclasses import dataclass, asdict
import time
from datetime import datetime

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
    link: str
    active_price: int
    rewiews: int
    # sold: int
    # catalog: str
    date_create: str


def get_one_card_data(driver, base_url):
    name = WebDriverWait(driver, 30). \
        until(EC.presence_of_element_located((
        (By.XPATH, ".//*[@data-widget='webProductHeading']"))))
    # name = driver.find_element(By.XPATH, ".//*[@data-widget='webProductHeading']").text

    layout = driver.find_elements(By.XPATH, ".//*[@data-widget='webReviewProductScore']")[0].text
    layout = layout.split('\n')
    rewiews = layout[0].split(' ')[0]

    try:
        cost_ozon = driver.find_element(By.XPATH, ".//*[@data-widget='webOzonAccountPrice']").text
    except:
        cost_ozon = driver.find_element(By.XPATH, ".//*[@data-widget='webPrice']").text
    cost_ozon_clen = cost_ozon.replace('\u2009', '').split('₽')[0]

    date_create = datetime.today().strftime("%d-%m-%Y")

    return Card(name.text, base_url, int(cost_ozon_clen), rewiews, date_create)


def save_file(data):
    path = 'C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\data\\Samura.csv'
    df = pd.DataFrame([data])
    print(df[df.columns[-3:]])
    df.to_csv(path, mode='a', index=False, header=False)
    print('>>>Сохранение завершено<<<')


def urls_monitoring(driver) -> pd.DataFrame:
    urls = [
        'https://www.ozon.ru/product/shef-nozh-dlya-narezki-myasa-ryby-ovoshchey-i-fruktov-kuhonnyy-nozh-povarskoy-nozh-dlya-kuhni-samura-163145300',
        'https://www.ozon.ru/product/generator-benzinovyy-portativnyy-lavada-g4000-elektrogenerator-benzoelektrostantsiya-3-3-3-5-819332872/?sh=1RJHcmpPdA',
        'https://www.ozon.ru/product/nabor-instrumentov-dlya-chistki-ushey-7-predmetov-instrument-dlya-chistki-ushey-526254914/?sh=1RJHcmMATA,'
        'https://www.ozon.ru/product/carte-noire-original-kofe-rastvorimyy-95-g-33871154/?sh=1RJHcmfaNg',
        'https://www.ozon.ru/product/domkrat-avtomobilnyy-podkatnoy-2t-v-keyse-domkrat-gidravlicheskiy-belak-bak-00531-150200129/?sh=1RJHcixAgg',
        'https://www.ozon.ru/product/zashchitnoe-steklo-prozrachnoe-dlya-ipad-7-8-9-10-2-2019-2020-2021-9h-0-3-mm-only-case-273831573/?sh=1RJHcvJyiA',
        'https://www.ozon.ru/product/nozh-santoku-dlya-narezki-myasa-ryby-ovoshchey-i-fruktov-yaponskiy-kuhonnyy-nozh-povarskoy-shef-163145302/?from_sku=163145300&oos_search=false&sh=1RJHcrl_Og',

    ]
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


if __name__ == '__main__':
    driver = init_webdriver(True)

    data = urls_monitoring(driver)
    save_db(data,
            name_db='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='Ozon')

    driver.quit()
