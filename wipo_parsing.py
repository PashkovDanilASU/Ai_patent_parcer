from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import os


def changeSelectOption(searching_by, searching_string, position):
    # Поиск
    button = driver.find_element(searching_by, searching_string)
    # Создаем объект Select для работы с элементом <select>
    select = Select(button)
    # Выбираем опцию
    select.select_by_value(position)
    time.sleep(5)


url = "https://patentscope.wipo.int/search/ru/result.jsf?_vid=P20-LK2O66-06230"

# Всякие предварительные настройки типо драйвер подключить для браузера(у нас хром)
service = Service(executable_path='./chromedriver.exe')
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

try:
    # Запуск браузера и открытие веб-страницы
    driver.maximize_window()
    driver.get(url)
    time.sleep(5)

    # В поле ввода пишем Artificial intelligence и жмем поиск
    search_form = driver.find_element(By.ID, "simpleSearchForm:fpSearch:input")
    search_form.clear()
    search_form.send_keys("Artificial intelligence")
    search_form.send_keys(Keys.ENTER)
    time.sleep(3)

    changeSelectOption(By.ID, "resultListCommandsForm:viewType:input", "DOUBLE_VIEW")
    changeSelectOption(By.ID, "resultListCommandsForm:perPage:input", "200")

    # Получаем HTML-код страницы с помощью Selenium
    html = driver.page_source

    # Создаем объект BeautifulSoup для парсинга HTML-кода
    soup = BeautifulSoup(html, "html.parser")

    # В цикле создается словарь данных для каждого патента
    for el in soup.find_all(class_="ps-patent-result"):
        patent = dict()
        patent["patent_title"] = el.find("span", class_="needTranslation-title").text
        patent["publication_date"] = el.select_one('span[id$="resultListTableColumnPubDate"]').text.strip()
        patent["document_number"] = el.find("span",
                                            class_="notranslate ps-patent-result--title--patent-number").text
        patent["patent_owner"] = el.find("span", class_="ps-field--value ps-patent-result--applicant notranslate").text
        patent["applicant"] = el.find("span", class_="ps-field--value ps-patent-result--inventor notranslate").text
        patent["international_patent_classification"] = el.select_one('span[id$="PCTipc"]').text.strip()
        patent["country"] = el.find("div", class_="ps-patent-result--title--ctr-pubdate").select_one("span").text.strip()
        print(patent)

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
