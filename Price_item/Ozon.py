from dataclasses import dataclass
import time
from datetime import datetime
from logger import init_logger, logger_obj
import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from driver import init_webdriver
from save_DB import save_db

log = init_logger('ozon')


@dataclass
class Card:
    name: str
    link: str
    active_price: int
    rewiews: int
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
        sold_out = driver.find_element(By.CLASS_NAME, 'kv8').text
        name = driver.find_element(By.CLASS_NAME, 'k5v')
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
            (By.XPATH, './/*[@data-widget="citySelector"]/div[2]/div/div/div'))).click()  # Клик на Железногорск из списка
        # driver.find_elements(By.CLASS_NAME, 'dr0')[0].click()
    else:
        raise Exception('Изменился путь к изменению Адреса доставки')


def urls_monitoring(driver) -> pd.DataFrame:
    urls = [
        'https://www.ozon.ru/product/polnoratsionnyy-suhoy-korm-s-govyadinoy-black-angus-dlya-domashnih-koshek-starshe-1-goda-1-2-kg-431298791/?oos_search=false',
        'https://www.ozon.ru/product/suhoy-korm-dlya-koshek-purina-one-adult-s-govyadinoy-s-tselnymi-zlakami-750-g-137590849',
        'https://www.ozon.ru/product/suhoy-korm-dlya-koshek-purina-one-s-vysokim-soderzhaniem-kuritsy-i-tselnymi-zlakami-9-75-kg-689850724',
        'https://www.ozon.ru/product/shef-nozh-dlya-narezki-myasa-ryby-ovoshchey-i-fruktov-kuhonnyy-nozh-povarskoy-nozh-dlya-kuhni-samura-163145300',
        'https://www.ozon.ru/product/generator-benzinovyy-portativnyy-lavada-g4000-elektrogenerator-benzoelektrostantsiya-3-3-3-5-819332872/?sh=1RJHcmpPdA',
        'https://www.ozon.ru/product/nabor-instrumentov-dlya-chistki-ushey-7-predmetov-instrument-dlya-chistki-ushey-526254914/?sh=1RJHcmMATA,'
        'https://www.ozon.ru/product/carte-noire-original-kofe-rastvorimyy-95-g-33871154/?sh=1RJHcmfaNg',
        'https://www.ozon.ru/product/domkrat-avtomobilnyy-podkatnoy-2t-v-keyse-domkrat-gidravlicheskiy-belak-bak-00531-150200129/?sh=1RJHcixAgg',
        'https://www.ozon.ru/product/zashchitnoe-steklo-prozrachnoe-dlya-ipad-7-8-9-10-2-2019-2020-2021-9h-0-3-mm-only-case-273831573/?sh=1RJHcvJyiA',
        'https://www.ozon.ru/product/nozh-santoku-dlya-narezki-myasa-ryby-ovoshchey-i-fruktov-yaponskiy-kuhonnyy-nozh-povarskoy-shef-163145302/?from_sku=163145300&oos_search=false&sh=1RJHcrl_Og',

    ]
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


if __name__ == '__main__':
    driver = init_webdriver(True)

    data = urls_monitoring(driver)
    save_db(data,
            path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='Ozon')

    driver.quit()
