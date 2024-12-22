import logging
import time
from datetime import datetime  # Импортируем datetime для работы с датами

from pytz import timezone
from selenium import webdriver  # Импортируем webdriver для управления браузером
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import (
    By,  # Импортируем модуль для выбора элементов по различным селекторам
)

from news.models import News  # Импортируем модель News для записи данных в базу данных


logger = logging.getLogger('main')


def parse_news() -> None:
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    try:
        driver = webdriver.Chrome(options=options)

    except Exception as e:
        logger.error(f'Ошибка при запуске WebDriver: {e}')
        return

    else:
        # Переходим на страницу новостей League of Legends
        driver.get('https://www.leagueoflegends.com/ru-ru/news/game-updates/')

        max_scrolls = 50
        scroll_count = 0

        # Скроллинг страницы, если новостей в базе данных ещё нет
        if not News.objects.exists():
            while scroll_count < max_scrolls:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(1)
                try:
                    button = driver.find_element(By.CLASS_NAME, 'cta')
                    button.click()
                    scroll_count += 1
                except NoSuchElementException:
                    break

        # Парсинг элементов страницы
        elements = driver.find_element(
            By.CSS_SELECTOR, "div[class='sc-1de19c4d-0 jhZjMa']"
        ).find_elements(By.TAG_NAME, 'a')

        # Получение существующих URL из базы данных
        news_url_set = set(News.objects.values_list('url', flat=True))

        # Обработка элементов и создание новых объектов
        news_objects = []
        for elem in elements:
            title = elem.find_element(By.CSS_SELECTOR, "div[class='sc-ce9b75fd-0 lmZfRs']").text
            date_published = elem.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
            date_object = (
                datetime.strptime(date_published[:10], '%Y-%m-%d')
                .astimezone(timezone('Europe/Moscow'))
                .date()
            )
            description = elem.find_element(By.CSS_SELECTOR, "div[class='sc-85c0bd82-0 faqZib']").text
            image_url = elem.find_element(By.TAG_NAME, 'img').get_attribute('src')
            news_url = elem.get_attribute('href')
            if news_url not in news_url_set:
                news_objects.append(
                    News(
                        title=title,
                        description=description,
                        url=news_url,
                        date_published=date_object,
                        image=image_url,
                    )
                )

        # Сохранение новых объектов в базу данных
        if news_objects:
            News.objects.bulk_create(news_objects)
            logger.info(f'Добавлено новостей: {len(news_objects)}')
        else:
            logger.info('Новых новостей нет')

    finally:
        driver.quit()
