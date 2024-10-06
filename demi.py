import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions


options = EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Edge(options=options)
driver.get('https://www.leagueoflegends.com/ru-ru/news/game-updates/')


elements = driver.find_element(By.CSS_SELECTOR, "div[class='sc-a15cc6aa-0 IphyG']").find_elements(By.TAG_NAME, 'a')
for elem in elements:
    title = elem.find_element(By.CSS_SELECTOR, "div[class='sc-ce9b75fd-0 lmZfRs']").text
    date_published = elem.find_element(By.CSS_SELECTOR, "div[class='sc-1177c637-3 dRCcfn']").text
    description = elem.find_element(By.CSS_SELECTOR, "div[class='sc-85c0bd82-0 faqZib']").text
    image = elem.find_element(By.TAG_NAME, 'img').get_attribute('src')
    print(title)
    print(date_published)
    print(description)
    print(image)
    print('__________')
