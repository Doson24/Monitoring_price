import pandas as pd

from driver import init_webdriver
from get_price_dns import select_city, parse_catalog, save_file, parse_card, Card
from selenium.webdriver.common.by import By
from datetime import datetime
from SqlLite import add_data

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def save_db(data: pd.DataFrame):
    add_data(data,
             name_db='online_markets.db',
             table_name='DNS')


def main():
    date = datetime.today().strftime("%d-%m-%Y")
    driver = init_webdriver(True)
    driver.get('https://www.dns-shop.ru/')
    try:
        city = select_city(driver)
    except:
        city = 'Ошибка'
    print(city, "г выбран")

    urls = {
        'Наушники TWS Apple AirPods Pro белый': 'https://www.dns-shop.ru/product/bf72ca16dcd1ed20/nausniki-tws-apple-airpods-pro-belyj/',
        'Наушники TWS Apple Airpods 3 белый': 'https://www.dns-shop.ru/product/411a5e8cdcd1ed20/nausniki-tws-apple-airpods-3-belyj/',
        'Наушники TWS Apple AirPods Pro 2 белый': 'https://www.dns-shop.ru/product/8264b1723015ed20/nausniki-tws-apple-airpods-pro-2-belyj/'
    }
    cards = []
    for name, url in urls.items():
        driver.get(url)
        if driver.current_url != url:
            driver.get(url)
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(1)

        price = WebDriverWait(driver, 30) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                   'div[class=product-buy__price]'))).text
        # price = int(price[:-2].replace(' ', ''))

        card = Card(name, url, date, city=city, active_price=price, prev_price='', catalog='')
        cards.append(card)
        print(f'[+] Данные {name} загружены')
    cards = pd.DataFrame(cards)
    save_db(cards)
    driver.quit()


if __name__ == '__main__':
    main()
