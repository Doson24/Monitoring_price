from Ozon_urls import top_products
from driver import init_webdriver
from datetime import datetime
from save_DB import save_db

if __name__ == '__main__':
    start = datetime.now()
    driver = init_webdriver(True)
    data = top_products(driver)
    save_db(data,
            path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='Ozon_top')
    print('Время выполнения: ', datetime.now() - start)
    driver.quit()