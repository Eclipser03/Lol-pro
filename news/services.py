from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions

from news.models import News


def parse_news():
    options = EdgeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Edge(options=options)
    driver.get('https://www.leagueoflegends.com/ru-ru/news/game-updates/')

    elements = driver.find_element(By.CSS_SELECTOR, "div[class='sc-a15cc6aa-0 IphyG']").find_elements(
        By.TAG_NAME, 'a'
    )
    for elem in elements:
        title = elem.find_element(By.CSS_SELECTOR, "div[class='sc-ce9b75fd-0 lmZfRs']").text
        date_published = elem.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
        date_object = (datetime.strptime(date_published[:10], '%Y-%m-%d')).date()
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

    print('successfuly parsing')


parse_news()
