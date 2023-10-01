from Ozon_functions import top_products
from driver import init_webdriver
from datetime import datetime
from save_DB import save_db

if __name__ == '__main__':
    start = datetime.now()
    driver = init_webdriver(True)
    top_products(driver)

    print('Время выполнения: ', datetime.now() - start)
    driver.quit()