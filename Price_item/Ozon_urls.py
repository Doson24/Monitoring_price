from Ozon_functions import monitoring_urls
from save_DB import save_db
from driver import init_webdriver
from datetime import datetime


if __name__ =="__main__":
    start = datetime.now()
    driver = init_webdriver(False)
    data = monitoring_urls(driver)
    save_db(data,
            path='C:\\Users\\user\\Desktop\\Projects\\Price_monitoring\\Price_item\\bat\\online_markets.db',
            table_name='Ozon')
    print('Время выполнения: ', datetime.now() - start)
    driver.close()