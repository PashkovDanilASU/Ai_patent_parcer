#from bs4 import BeautifulSoup
#import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

# Всякие предварительные настройки типо драйвер подключить для браузера(у нас хром)
service = Service(executable_path='./chromedriver.exe')
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
url = "https://searchplatform.rospatent.gov.ru/patents"
# driver.get(url)
driver.maximize_window()
html = driver.page_source

try:
    count_parcing = 0  # добавил счетчик для подсчета количества полей обработанных парсером
    driver.get(url)
    time.sleep(3)
    input_field = driver.find_element(By.ID, "simple_search_input").send_keys("искусственный интеллект")
    button = driver.find_element(By.CLASS_NAME, "search_button")
    button.click()
    time.sleep(3)
    amount_patents = driver.find_element(By.XPATH,'/html/body/div/div/div[3]/div/div[4]/div[3]/span')
    amount_patents = int((amount_patents.text).split()[-1])

    button = driver.find_element(By.XPATH,
                                 "/ html / body / div / div / div[3] / div / div[4] / div[3] / div / div[2] / div[2] / div")
    button.click()
    time.sleep(1)

    button = driver.find_element(By.XPATH,
                                 "/ html / body / div / div / div[3] / div / div[4] / div[3] / div / div[2] / div[2] / div / ul / li[3]")
    button.click()
    time.sleep(1)

    button = driver.find_element(By.XPATH,
                                 "/ html / body / div / div / div[3] / div / div[4] / div[3] / div / div[3] / div[2] / div")
    button.click()
    time.sleep(1)
    
    button = driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div/div[4]/div[3]/div/div[3]/div[2]/div/ul/li[4]")
    el_per_page = int(button.text)
    page_scrolling = (amount_patents + el_per_page - 1) // el_per_page
    button.click()
    time.sleep(1)

    for i in range(page_scrolling):  # Не попадает в условие if - помочь братку
        # Делаем дела парсим шмарсим на конкретной страничке - ТЕБЕ СЮДА ЧЕТО ДОБАВИТЬ
        table_ = driver.find_element(By.CLASS_NAME,
                                         "table_default")  # Класс table_default, где располагаются поля таблицы. Класс table_default находится в классе "content_flex content_flex_outer".

        informations = table_.find_elements(By.TAG_NAME,
                                                "td")  # Считывает все тэги в таблице (должно быть 700 (т.к. 7 столбцов у каждого патента, а отображается 100 патентов), выходит 700)

        for information in informations:  # Считываем информацию из тэгов (то есть данные самого патента, в данном цикле считываются 100 патентов подряд)
            count_new_line = +1
            patent_data = information.text
            print(patent_data)
            count_parcing += 1
            if count_parcing % 7 == 0:
                print()
        time.sleep(1)
        footer = driver.find_element(By.CLASS_NAME, "pagNextPage_ru")
        delta_y = footer.rect['y']
        ActionChains(driver) \
            .scroll_by_amount(0, delta_y) \
            .perform()
        time.sleep(4)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        wait = WebDriverWait(driver, 1)
        ###find_next_element = driver.find_element(By.CLASS_NAME,
                                      ###   "pagNextPage_ru")
        find_next_element = wait.until(EC.element_to_be_clickable((
            By.CLASS_NAME,
                "pagNextPage_ru"))) # полный путь до кнопки > отвечающей за переход на следующую страницу + ожидание кликабельности(чтоб сайт успел прогрузить и не выдал ошибку
        # NoSuchElement
        ###find_next_element.click()
        find_next_element = driver.find_element(By.CLASS_NAME, "pagNextPage_ru") # Ищем кнопку перехода на некст страницу патентов
        find_next_element.click()
        time.sleep(1)

    time.sleep(10)
except Exception as _ex:
    print(_ex)

finally:
    #print(count_parcing)
    driver.close()
    driver.quit()

