#from bs4 import BeautifulSoup
#import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date
import time
import json

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
    zero_date = date(2000,1,1) # нулевая дата для добавления в "конструктор" патента
    all_patents_list = []  # Создаю пустой список, где будут находится все патенты (обращение к элементам списка по индексам начиная с 0)
    all_patents_list_true =[]
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
    for i in range(page_scrolling):
        table_ = driver.find_element(By.CLASS_NAME,
                                         "table_default")  # Класс table_default, где располагаются поля таблицы. Класс table_default находится в классе "content_flex content_flex_outer".

        informations = table_.find_elements(By.TAG_NAME,
                                                "td")  # Считывает все тэги в таблице (должно быть 700 (т.к. 7 столбцов у каждого патента, а отображается 100 патентов), выходит 700)

        for information in informations:  # Считываем информацию из тэгов (то есть данные самого патента, в данном цикле считываются 100 патентов подряд)
            if count_parcing % 7 == 0:
                patent = {'patent_number': '_', 'patent_publication_date': zero_date, 'patent_name': '_', 'applicant': '_',
                           'author': '_',
                           'copyright_holder': '_', 'mpc_index': '_', 'spk_index': '_'} # конструктор патента, который не содержит особой информации
                all_patents_list.append(patent)
            patent_data = information.text
            if count_parcing % 7 == 0: #Здесь разделяется информация про номер патента и дата его публикации
                if '0' in patent_data[-5] and '0' in patent_data[-2]:
                    patent_data_date = date(int(patent_data[-10:-6]), int(patent_data[-4]), int(patent_data[-1]))
                elif '0' in patent_data[-5] and '0' not in patent_data[-2]:
                    patent_data_date = date(int(patent_data[-10:-6]), int(patent_data[-4]), int(patent_data[-2:]))
                elif '0' not in patent_data[-5] and '0' in patent_data[-2]:
                    patent_data_date = date(int(patent_data[-10:-6]), int(patent_data[-5:-3]), int(patent_data[-1]))
                else:
                    patent_data_date = date(int(patent_data[-10:-6]), int(patent_data[-5:-3]), int(patent_data[-2:]))
                patent_data = patent_data[:-10].strip()
                patent['patent_number'] = patent_data
                patent['patent_publication_date'] = patent_data_date.isoformat()
            elif count_parcing % 7 == 1: # Далее идет каскад условий, какому ключу словаря (патента) присвоить его значение поля
                patent['patent_name'] = patent_data
            elif count_parcing % 7 == 2:
                patent['applicant'] = patent_data
            elif count_parcing % 7 == 3:
                patent['author'] = patent_data
            elif count_parcing % 7 == 4:
                patent['copyright_holder'] = patent_data
            elif count_parcing % 7 == 5:
                patent['mpc_index'] = patent_data
            else:
                patent['spk_index'] = patent_data
            count_parcing += 1
        time.sleep(1)
        if i == 9: # здесь сохраняем акутальные патенты в json файл
            for patent_ in all_patents_list:
                if patent_['applicant'] == '—' or patent_['author'] == '—' or patent_['copyright_holder'] == '—':
                    continue
                else:
                    all_patents_list_true.append(patent_)
            del all_patents_list #удаляю старый список, для очистки памяти
            with open("all_patents_list_true.json", "w", encoding="utf-8") as file:
                json.dump(all_patents_list_true, file, indent=4, ensure_ascii=False)
            #print(all_patents_list_true)
             #здесь добавлено чтени из json файла, чтобы перезаписать словарь (в котором будут находиться акутальные патенты)
            with open("all_patents_list_true.json", "r",  encoding="utf-8") as file:
                data = json.load(file)
                for obj in data:
                    patent = {}
                    patent['patent_number'] = obj['patent_number']
                    #
                    date_string = obj['patent_publication_date']
                    date_python = date.fromisoformat(date_string)
                    #
                    patent['patent_publication_date'] = date_python
                    patent['patent_name'] = obj['patent_name']
                    patent['applicant'] = obj['applicant']
                    patent['author'] = obj['author']
                    patent['copyright_holder'] = obj['copyright_holder']
                    patent['mpc_index'] = obj['mpc_index']
                    patent['spk_index'] = obj['spk_index']
                    all_patents_list_true.append(patent)
            #print(all_patents_list_true)
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
