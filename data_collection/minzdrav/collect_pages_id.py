from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By


def scroller(agent, scroll_pause_time = 2):
    last_height = agent.execute_script("return document.body.scrollHeight")

    while True:
        agent.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(scroll_pause_time)
        new_height = agent.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height



if __name__ == '__main__':
    URL = 'https://cr.minzdrav.gov.ru/clin_recomend'

    driver = webdriver.Firefox()
    driver.get(URL)

    scroller(driver)
    elements = driver.find_elements(by=By.XPATH, value='//a[starts-with(@href, "/recomend")]')
    identifications = list(set([item.get_attribute('href').split('/')[-1] for item in elements]))

    with open('identifications.txt', 'w', encoding='utf-8') as file:
        for item in identifications:
            file.write(f'{item}\n')

    driver.close()
