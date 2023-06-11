from driver import init_webdriver
from DNS import urls_monitoring
from save_DB import save_db

if __name__ == '__main__':
    driver = init_webdriver(True)
    driver.get('https://www.dns-shop.ru/')

    products = {
        'Наушники TWS Apple AirPods Pro белый': 'https://www.dns-shop.ru/product/bf72ca16dcd1ed20/nausniki-tws-apple-airpods-pro-belyj/',
        'Наушники TWS Apple Airpods 3 белый': 'https://www.dns-shop.ru/product/411a5e8cdcd1ed20/nausniki-tws-apple-airpods-3-belyj/',
        'Наушники TWS Apple AirPods Pro 2 белый': 'https://www.dns-shop.ru/product/8264b1723015ed20/nausniki-tws-apple-airpods-pro-2-belyj/'
    }

    data = urls_monitoring(driver, products)
    save_db(data, table_name='Airpods_Dns')

    driver.quit()
