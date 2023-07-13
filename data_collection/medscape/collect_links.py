import requests
from bs4 import BeautifulSoup as Bs
from selenium import webdriver
from selenium.webdriver.common.by import By


def scroll_to_xpath(agent, xpath):
    next_button = agent.find_element_by_xpath(xpath)
    agent.execute_script("arguments[0].scrollIntoView();", next_button)
    return next_button


def save(drugs):
    with open('./links.txt', 'w', encoding='utf-8') as file:
        for link in drugs:
            file.write(link+'\n')


def parse():
    output = []
    driver = webdriver.Firefox()

    home = 'https://reference.medscape.com/drugs'
    resp = requests.get(home).text
    driver.get(home)
    root = Bs(resp, 'html.parser').find('ul', class_='classdruglist').find_all('li')
    try:
        for element in root:
            print(f'[{root.index(element)}/{len(root)}]', element.a['href'], end='\t')
            element = element.a['href']

            driver.get(element)
            try:
                driver.find_element(
                    by=By.XPATH,
                    value='//span[@class="sort-link category"]'
                ).click()
            except Exception:
                pass

            driver.find_element(
                by=By.XPATH,
                value='//div[@class="topic-list sections active"]/span'
            ).click()
            soup = Bs(driver.page_source, 'html.parser')
            topics = [
                div.find_all('li') for div in soup.find_all('div', class_='topic-section expanded')
            ]

            for topic in topics:
                for medicament in topic:
                    medicament = medicament.a['href']
                    if medicament not in output:
                        output.append(medicament)
            print(len(list(set([m for topic in topics for m in topic ]))))
    finally:
        save(output)
        driver.close()


if __name__ == '__main__':
    parse()
