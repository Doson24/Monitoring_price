import datetime

import pandas as pd
from driver import init_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_data(driver, url):
    driver.get(url)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(1)

    price = driver.find_element(By.XPATH, '//*[@data-test-card-new-price]').text
    discount = price
    no_discount = driver.find_element(By.XPATH, '//*[@data-test-card-old-price]').text

    el_name = driver.find_element(By.XPATH, '//*[@data-test-card-name]')
    name = el_name.get_attribute('data-test-card-name')
    # feedback = get_name[1]

    date = datetime.datetime.today().strftime('%Y-%m-%dT%H:%M')
    data = pd.DataFrame([{
        'name': name,
        'discount': discount,
        'no discount': no_discount,
        # 'feedback': feedback,
        'create_date': date
    }])
    return data


if __name__ == '__main__':
    driver = init_webdriver(headless=True)
    url = 'https://krasnoyarsk.askona.ru/matrasy/astoria.htm/?SELECTED_HASH_SIZE=160x200-af13bfd624e1acd34f2103481efea402&SELECTED_FABRIC_ID=0'

    data = get_data(driver, url)
    print(data)
    print('>>>Сохранение<<<')
    path = 'C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\data\\askona.csv'
    data.to_csv(path, mode='a', index=False, header=False)
