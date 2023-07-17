from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from src.database_manager import session_maker
from src.database_manager import insert_patent, insert_log
import time, datetime
import os


def main(session):
    def changeSelectOption(searching_by, searching_string, position, sec):
        '''
        Изменение выбранного параметра выбранного элемента

        :param searching_by: Метод, используемый для поиска элемента. Допустимые значения: 'id', 'class_name', 'name', 'tag_name', 'css_selector' или 'xpath'.
        :param searching_string: Значение, используемое для поиска элемента на основе указанного метода поиска.
        :param position: Значение опции, которую нужно выбрать.
        :param sec: Время ожидания после установки поля
        :return: None
        '''
        # Поиск
        button = driver.find_element(searching_by, searching_string)
        # Создаем объект Select для работы с элементом <select>
        select = Select(button)
        # Выбираем опцию
        select.select_by_value(position)
        time.sleep(sec)

    def validateQuery(query):
        '''
        Функция для валидации данных при парсинге сайта для каждого поля патента
        Чтобы не было лишних символов, приходил None, вместо "\n" и т.д.

        :param query: Наш запрос к html коду патента
        :return: query_result
        '''

        query_result = query
        if not query_result:
            return None
        query_result = query_result.text.strip()
        if not query_result:
            return None
        return query_result

    def parseEveryPage():
        '''
        Основная функция парсинга.

        :return: Словарь log, содержащий информацию о завершении, процессе парсинга.
        '''

        def parsePage():
            '''
            Парсит каждую страницу и извлекает информацию о патентах.

            :return: None
            '''

            # Получаем HTML-код страницы с помощью Selenium
            html = driver.page_source
            # Создаем объект BeautifulSoup для парсинга HTML-кода
            soup = BeautifulSoup(html, "html.parser")

            # В цикле создается словарь данных для каждого патента
            for el in soup.find_all(class_="ps-patent-result"):
                patent = dict()
                patent_title = validateQuery(el.find("span", class_="needTranslation-title"))
                patent["patent_title"] = patent_title.capitalize() if patent_title else None
                patent["publication_date"] = validateQuery(el.select_one('span[id$="resultListTableColumnPubDate"]'))
                patent["document_number"] = validateQuery(
                    el.find("span", class_="notranslate ps-patent-result--title--patent-number"))
                patent["patent_owner"] = [validateQuery(
                    el.find("span", class_="ps-field--value ps-patent-result--applicant notranslate"))]
                patent["applicant"] = [validateQuery(
                    el.find("span", class_="ps-field--value ps-patent-result--inventor notranslate"))]
                patent["international_patent_classification"] = [validateQuery(el.select_one('span[id$="PCTipc"]'))]
                patent["country"] = validateQuery(
                    el.find("div", class_="ps-patent-result--title--ctr-pubdate").select_one("span"))

                # Если отсутствует хотя бы одно обязательное поле, патент в базу не идет
                if not patent.get("patent_title") or not patent.get("publication_date") or \
                        not patent.get("international_patent_classification"):
                    log['missed_patents_count'] += 1
                    continue

                # Вместо этого принта будет запись патента в базу данных
                insert_patent(session, patent)
                log["parsed_patents_count"] += 1

        def nextPage():
            '''
            Переходит на следующую страницу и возвращает статус перехода.

            :return: True, если переход выполнен успешно. False, если больше нет следующей страницы.
            '''
            next_button = False
            # Попытка найти неактивную кнопку на следующую страницу
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".js-paginator-next.ui-state-disabled")
            except:
                pass
            # Если таковую нашли, значит данная страница последняя
            if next_button:
                return False
            # Если это не так, то ищем активную кнопку на следующую страницу и жмем её
            next_button = driver.find_element(By.CLASS_NAME, "js-paginator-next")
            next_button.click()
            time.sleep(1)
            return True

        try:
            while True:
                parsePage()
                if not nextPage():
                    log['status'] = 'Parsing completed'
                    log['timestamp'] = datetime.datetime.utcnow()
                    return log

        except Exception as e:
            log['status'] = 'Parsing error: {}'.format(str(e))
            log['timestamp'] = datetime.datetime.utcnow()
            return log

    def configureSearch(search_term):
        '''
        Выполняет предварительную настройку сайта

        :param search_term: Поисковой запрос, по которому будет парсится сайт
        :return: None
        '''

        # Запуск браузера и открытие веб-страницы
        driver.maximize_window()
        driver.get(url)
        time.sleep(5)

        # настройка поиска на сайте по любому полю, а не только в заголовке
        changeSelectOption(By.ID, "simpleSearchForm:field:input", "RU_ALL", 1)
        # Ищем поле ввода поиска на сайте
        search_form = driver.find_element(By.ID, "simpleSearchForm:fpSearch:input")
        # В поле ввода пишем Artificial intelligence и жмем поиск
        search_form.clear()
        search_form.send_keys(search_term)
        search_form.send_keys(Keys.ENTER)
        time.sleep(3)

        changeSelectOption(By.ID, "resultListCommandsForm:viewType:input", "DOUBLE_VIEW", 3)
        changeSelectOption(By.ID, "resultListCommandsForm:perPage:input", "200", 5)

    # Логирование парсера, в log будет содержаться информация о парсинге сайта
    log = {
        'parsed_patents_count': 0,
        'missed_patents_count': 0,
        'status': 'Parsing in progress',
        'timestamp': None
    }

    # Домен сайта с патентами
    url = "https://patentscope.wipo.int/search/ru/result.jsf?_vid=P20-LK2O66-06230"

    # Предварительные настройки: драйвер подключить для браузера(хром)
    service = Service(executable_path='chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        configureSearch("Искусственный интеллект")
        log = parseEveryPage()
        print(log)
        insert_log(session, log)

    except Exception as ex:
        log['status'] = 'Parsing error: {}'.format(str(ex))
        log['timestamp'] = datetime.datetime.utcnow()
        print(ex)
    finally:
        driver.close()
        driver.quit()


if __name__ == "__main__":
    with session_maker() as session:
        main(session)
        session.commit()
