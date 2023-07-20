from Citylink import get_items_catalog
from driver import init_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_url_catalogs(driver):
    base_url = 'https://www.citilink.ru/'
    driver.get(base_url)
    driver.set_window_size(1920, 1080)

    driver.find_element(By.XPATH, '//*[@data-meta-name="DesktopHeaderFixed__catalog-menu"]').click()
    driver.implicitly_wait(3)
    menu = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@data-meta-name="CatalogMenuDesktopLayout__menu"]')))
    # menu = driver.find_element(By.XPATH, '//*[@data-meta-name="CatalogMenuDesktopLayout__menu"]')
    menu_items = menu.find_elements(By.XPATH, './/*[@data-meta-name="DesktopMenu__category--menu-item"]')
    items_link = get_link(menu_items)

    catalogs_links = []
    for item_link in items_link[:-3]:  # убираем Уцененнные товары, Сертификаты, Сервис и услуги
        driver.get(item_link)
        cards_layout = driver.find_element(By.XPATH, './/*[@data-meta-name="CategoryCardsLayout"]')
        catalogs = cards_layout.find_elements(By.XPATH, './/a[contains(@class, "app-catalog")]')
        for catalog in catalogs:
            link = catalog.get_attribute('href')
            name = catalog.text
            catalogs_links.append(link)
            print(name, link)
        print('_' * 60)
        # time.sleep(1)
        driver.implicitly_wait(1)
    return catalogs_links


def get_link(menu_items):
    return [item_menu.get_attribute('href') for item_menu in menu_items]


def save_urls(base_urls):
    with open('links.txt', 'w') as f:
        for url in base_urls:
            f.write(url + "\n")


def load_urls():
    with open('links.txt', 'r') as f:
        data = f.readlines()
    return data


if __name__ == '__main__':
    driver = init_webdriver(True)

    # base_urls = get_url_catalogs(driver)
    # save_urls(base_urls)
    base_urls = load_urls()

    print('[+] Количество каталогов ', len(base_urls))
    get_items_catalog(driver, base_urls=base_urls[2:], table_name='All_Citylink')
