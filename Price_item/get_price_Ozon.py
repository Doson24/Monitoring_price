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


@dataclass
class Card:
    name: str
    link: str
    price: int
    rewiews: str
    # sold: int
    # catalog: str
    date_create: str


def get_one_card_data(driver, base_url):
    driver.get(base_url)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(3)
    name = WebDriverWait(driver, 30). \
        until(EC.presence_of_element_located((
        (By.XPATH, ".//*[@data-widget='webProductHeading']"))))
    # name = driver.find_element(By.XPATH, ".//*[@data-widget='webProductHeading']").text

    layout = driver.find_elements(By.XPATH, ".//*[@data-widget='webReviewProductScore']")[0].text
    layout = layout.split('\n')
    rewiews = layout[0]

    try:
        cost_ozon = driver.find_element(By.XPATH, ".//*[@data-widget='webOzonAccountPrice']").text
    except:
        cost_ozon = driver.find_element(By.XPATH, ".//*[@data-widget='webPrice']").text
    cost_ozon_clen = cost_ozon.replace('\u2009', '').split('₽')[0]

    date_create = datetime.today().strftime("%d-%m-%Y")

    return Card(name.text, base_url, int(cost_ozon_clen), rewiews, date_create)


def save_file(data, filename='data\\Samura.csv'):
    df = pd.DataFrame([data])
    print(df[df.columns[-3:]])
    df.to_csv(filename, mode='a', index=False, header=False)
    print('>>>Сохранение завершено<<<')


if __name__ == '__main__':
    # main()
    driver = init_webdriver(True)

    url = 'https://www.ozon.ru/product/shef-nozh-dlya-narezki-myasa-ryby-' \
          'ovoshchey-i-fruktov-kuhonnyy-nozh-povarskoy-nozh-dlya-kuhni-samura' \
          '-163145300/'
    data = get_one_card_data(driver, url)
    save_file(asdict(data))

    driver.quit()
