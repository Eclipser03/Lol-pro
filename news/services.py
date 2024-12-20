import logging
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import (
    By,  # Импортируем модуль для выбора элементов по различным селекторам
)


logger = logging.getLogger('main')


def parse_news():
    from datetime import datetime  # Импортируем datetime для работы с датами

    from selenium import webdriver  # Импортируем webdriver для управления браузером

    # from selenium.webdriver.edge.options import (
    #     Options as EdgeOptions,  # Импортируем настройки Edge для создания экземпляра браузера
    # )
    from selenium.webdriver.chrome.options import Options

    from news.models import News  # Импортируем модель News для записи данных в базу данных

    # Устанавливаем параметры для Edge, чтобы отключить ненужные логи
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Создаем экземпляр браузера Edge с заданными настройками
    # driver = webdriver.Edge(options=options)
    driver = webdriver.Chrome(options=options)

    # Переходим на страницу новостей League of Legends
    driver.get('https://www.leagueoflegends.com/ru-ru/news/game-updates/')

    # Получаем начальную высоту страницы (чтобы отслеживать изменения высоты после подгрузки контента)
    # last_height = driver.execute_script('return document.body.scrollHeight')

    if not News.objects.exists():
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1)
            try:
                button = driver.find_element(By.CLASS_NAME, 'cta')
                button.click()
            except NoSuchElementException:
                break

    elements = driver.find_element(By.CSS_SELECTOR, "div[class='sc-1de19c4d-0 jhZjMa']").find_elements(
        By.TAG_NAME, 'a'
    )
    for elem in elements:
        title = elem.find_element(By.CSS_SELECTOR, "div[class='sc-ce9b75fd-0 lmZfRs']").text
        date_published = elem.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
        date_object = (datetime.strptime(date_published[:10], '%Y-%m-%d')).date()  # noqa: DTZ007
        description = elem.find_element(By.CSS_SELECTOR, "div[class='sc-85c0bd82-0 faqZib']").text
        image_url = elem.find_element(By.TAG_NAME, 'img').get_attribute('src')
        news_url = elem.get_attribute('href')
        if not News.objects.filter(url=news_url).exists():
            News.objects.create(
                title=title,
                description=description,
                url=news_url,
                date_published=date_object,
                image=image_url,
            )
            logger.info('Добавлена новость')

    print('Парсинг завершён успешно')
    driver.quit()
