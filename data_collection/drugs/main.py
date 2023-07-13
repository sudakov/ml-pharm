import json
import os
import sys
import time
import traceback

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

CHECKED_FOOD_INTERACTION = []
EXECUTABLE_PATH = r'chromedriver.exe'
PATH_TO_FILE_WITH_LINKS = r'data/links.txt'
PATH_TO_FILE_WITH_LINKS_NO_COLLECTION = r'not_links.txt'

useragent = UserAgent()
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={useragent.random}")
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"


def get_all_urls(path):
    with open(path, 'r', encoding='utf-8') as f:
        urls = f.readlines()

    return [item.replace('\n', '') for item in urls]


def get_name(url):
    name = url[::-1]
    name = name[name.find(".") + 1: name.find("/")]

    return name[::-1]


def find_and_click_link(text, driver):
    element = driver.find_element(By.XPATH, f'//a[contains(text(), "{text}")]')
    driver.execute_script("arguments[0].click();", element)


def close_extra_window(driver):
    try:
        close = driver.find_element(By.CLASS_NAME, "ddc-modal-close")
        close.click()
    except NoSuchElementException:
        pass


def parse_interactions(url, driver, driver2):
    driver.get(url)
    time.sleep(1)
    # Может вылезти баннер, который нужно закрыть
    close_extra_window(driver)

    # Возможно отсутствие нужной ссылки
    try:
        find_and_click_link("drug interactions", driver)
    except NoSuchElementException:
        print("No interactions here!")
        return None

    interaction_url = driver.current_url
    interactions = {
        'source': driver.current_url,
        'medications': [],
        'food': [],
        'disease': []
    }

    # На странице может не оказаться заболеваний и противопоказаний с ними
    try:
        interactions['disease'] = check_diseases(driver)
        driver.get(interaction_url)
    except NoSuchElementException:
        driver.get(interaction_url)
    close_extra_window(driver)
    # На странице может не оказаться взаимодействий с алкологем и едой
    try:
        food = check_food_and_alcohol(driver)
        interactions['food'] = food
        driver.get(interaction_url)
    except NoSuchElementException:
        driver.get(interaction_url)
    close_extra_window(driver)
    m, f = check_all_medications(driver, driver2, interactions['food'])
    interactions['medications'] = m
    interactions['food'] = f if f else interactions['food']

    return interactions


def check_diseases(driver):
    diseases = []
    find_and_click_link("disease interactions", driver)
    time.sleep(5)
    elements = driver.find_elements(By.CLASS_NAME, "interactions-reference")
    for element in elements:
        disease = {
            'source': driver.current_url
        }
        html_ = element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_, "html.parser")

        substances_and_disease = soup.find("h3")
        str = substances_and_disease
        substances_and_disease = substances_and_disease.text
        # if len(substances_and_disease) == 2:
        #     substance = substances_and_disease[0].split("(")[0].lstrip().rstrip()
        #     disease["main"] = substance
        #     name = substances_and_disease[1].lstrip().rstrip()
        # else:
        #     substances_and_disease = str.text.split("-")
        #     substance = substances_and_disease[0].split("(")[0].lstrip().rstrip()
        #     disease["main"] = substance
        #     name = substances_and_disease[1].lstrip().rstrip()
        separator = soup.find("span", class_="ddc-text-weight-normal").text
        substances_and_disease = substances_and_disease.split(separator)
        substance = substances_and_disease[0]
        name = substances_and_disease[1]
        disease["main"] = substance
        disease["interaction_with"] = name
        # print("MED:", substance, "\nDIS:", substances_and_disease[1])

        status = driver.find_element(
            By.XPATH, "//span[starts-with(@class, 'ddc-status-label status')]"
        )
        disease["classification_type"] = status.text
        disease["references"] = get_references(driver)
        disease.update(find_disease_recommendations(soup))

        diseases.append(disease)

    time.sleep(2)

    return diseases


def find_disease_recommendations(soup):
    recommendations = soup.find_all("p")

    return {
        'comment': recommendations[0].text,
        'desciption': recommendations[1].text
    }


def check_food_and_alcohol(driver):
    food_and_alcohol_list = []
    find_and_click_link("alcohol/food interactions", driver)
    driver.get(f'{driver.current_url}"?professional=1"')
    time.sleep(1)
    elements = driver.find_elements(By.CLASS_NAME, "interactions-reference")
    for element in elements:
        food_and_alcohol = {
            'source': driver.current_url
        }
        html_ = element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_, "html.parser")

        substances = soup.find("h3")
        if not substances:
            continue
        substances = substances.get_text()
        substances = substances.split("\t")
        subs = []
        for s in substances:
            if s != "\n" and s != "":
                subs.append(s.lstrip().rstrip())
        substances = subs
        if len(substances) == 1:
            substances[0] = substances[0].split("food")[0]
            substances.append("food")
        subs = []
        for s in substances:
            s = s.lstrip().rstrip()
            subs.append(s)
        substances = subs
        food_and_alcohol["main"] = substances[0]
        food_and_alcohol["interaction_with"] = substances[1]

        status = driver.find_element(
            By.XPATH, "//span[starts-with(@class, 'ddc-status-label')]"
        )
        food_and_alcohol["classification_type"] = status.text
        food_and_alcohol["references"] = get_references(driver)
        food_and_alcohol.update(find_food_and_alcohol_recommendations(soup))

        food_and_alcohol_list.append(food_and_alcohol)

    time.sleep(2)

    return food_and_alcohol_list


def find_food_and_alcohol_recommendations(soup):
    recommendations = soup.find_all("p")

    return {
        'comment': recommendations[0].text,
        'desciption': recommendations[1].text
    }


def check_all_medications(driver, driver2, food_interactions):
    time.sleep(10)
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(5)
    try:
        find_and_click_link("medication", driver)
        time.sleep(5)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(5)
        major_medications = driver.find_elements(By.CLASS_NAME, "int_3")
        moderate_medications = driver.find_elements(By.CLASS_NAME, "int_2")
        minor_medications = driver.find_elements(By.CLASS_NAME, "int_1")
    except Exception:
        print("No link")
        major_medications = driver.find_elements(
            By.XPATH, "//ul[@class='interactions ddc-list-unstyled']/li[@class='int_3']"
        )
        moderate_medications = driver.find_elements(
            By.XPATH, "//ul[@class='interactions ddc-list-unstyled']/li[@class='int_2']"
        )
        minor_medications = driver.find_elements(
            By.XPATH, "//ul[@class='interactions ddc-list-unstyled']/li[@class='int_1']"
        )
        all_medications = major_medications + moderate_medications + minor_medications

        if len(all_medications) == 0:
            major_medications = driver.find_elements(By.CLASS_NAME, "int_3")
            moderate_medications = driver.find_elements(By.CLASS_NAME, "int_2")
            minor_medications = driver.find_elements(By.CLASS_NAME, "int_1")

    all_medications = major_medications + moderate_medications + minor_medications

    # В all_medications присутсвуют лишние элементы, на которые мы будем все равно переходить, 
    # но не будем собирать информацию
    medications_result = []
    food_result = food_interactions
    for medication in all_medications:
        # url = driver.current_url
        html_ = medication.get_attribute('innerHTML')
        soup = BeautifulSoup(html_, "html.parser")
        link = "https://www.drugs.com" + soup.find("a").get("href") + "?professional=1"
        try:
            m, f = check_one_medication(link, driver2, food_result)
            medications_result += m
            food_result += f
        except Exception:
            pass

    return medications_result, food_result


def check_one_medication(link, driver2, all_food):
    driver2.get(link)
    time.sleep(2)
    elements = driver2.find_elements(By.CLASS_NAME, "interactions-reference-wrapper")
    medications = []
    food = []
    for element in elements:
        html_ = element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_, "html.parser")
        substances = soup.find("h3")
        if not substances:
            continue
        substances = substances.get_text()
        substances = substances.split("\t")
        subs = []
        for s in substances:
            if s != "\n" and s != "":
                subs.append(s.lstrip().rstrip())
        substances = subs
        if len(substances) == 1:
            substances[0] = substances[0].split("food")[0]
            substances.append("food")
        subs = []
        for s in substances:
            s = s.lstrip().rstrip()
            subs.append(s)
        substances = subs
        # substances - Список из двух слов (главное вещество и то, с которым оно взаимодействует)
        # print(substances, "\n\n")
        if substances[1] == "food":
            if substances[0] not in CHECKED_FOOD_INTERACTION:
                CHECKED_FOOD_INTERACTION.append(substances[0])
                food_properties = {
                    "main": substances[0],
                    "interaction_with": substances[1]
                }
                status = driver2.find_element(
                    By.XPATH, "//span[starts-with(@class, 'ddc-status-label status')]"
                )
                food_properties["classification_type"] = status.text
                food_properties = find_food_recommendations(soup, food_properties)
                food_properties["references"] = get_references(driver2)
                food_properties["source"] = driver2.current_url

                food_full = all_food + food
                if food_properties not in food_full:
                    food.append(food_properties)
        else:
            med_properties = {
                "main": substances[0],
                "interaction_with": substances[1]
            }
            status = driver2.find_element(
                By.XPATH, "//span[starts-with(@class, 'ddc-status-label status')]"
            )
            med_properties["classification_type"] = status.text
            med_properties = find_med_recommendations(soup, med_properties)
            med_properties["references"] = get_references(driver2)
            med_properties["source"] = driver2.current_url
            medications.append(med_properties)

    return medications, food


def find_food_recommendations(soup, food_properties):
    recommendations = soup.find_all("p")
    recommendations = recommendations[1].text
    recommendations = recommendations.split("\n\n")
    food_rec_types = ["generally avoid", "adjust dosing interval", "management", "monitor"]
    description = {}
    for recommendation in recommendations:
        type_exists = False
        for type_ in food_rec_types:
            if type_.upper() in recommendation:
                description["_".join(type_.split())] = recommendation.replace(type_.upper() + ": ", "")
                type_exists = True
        if not type_exists:
            description["Other recommendation"] = recommendation
    food_properties["description"] = description

    return food_properties


def find_med_recommendations(soup, med_properties):
    recommendations = soup.find_all("p")
    recommendations = recommendations[1].text
    recommendations = recommendations.split("\n\n")
    med_rec_types = ["generally avoid", "adjust dosing interval", "management", "monitor"]
    description = {}
    for recommendation in recommendations:
        type_exists = False
        for type_ in med_rec_types:
            if type_.upper() in recommendation:
                description[type_] = recommendation.replace(type_.upper() + ": ", "")
                type_exists = True
        if not type_exists:
            description["Other recommendation"] = recommendation
    med_properties["description"] = description

    return med_properties


def get_references(browser):
    try:
        button = browser.find_element(
            By.XPATH, "//a[contains(text(), 'View all') and contains(text(), 'references')]"
        )
        button.click()
    except Exception:
        pass
    references = browser.find_elements(
        By.XPATH, "//div[starts-with(@class, 'ddc-reference-list')]/ol/li"
    )

    references = list(set([item.text for item in references]))

    return references


def check_fullness(j_file):
    with open(j_file, "r") as file:
        dictionary = json.load(file)
    name = os.path.basename(j_file)
    if not dictionary["interactions"]["medications"] and not dictionary["interactions"]["food"]:
        print(name, " loading...")
        return name, dictionary
    else:
        print(name, " is full")
        return None, None


def main(driver, driver2):
    if os.path.exists("medications"):
        pass
    else:
        os.mkdir("medications")
    collected_list = os.listdir("medications")
    # os.chdir("medications")
    no_collection_required = get_all_urls(PATH_TO_FILE_WITH_LINKS_NO_COLLECTION)
    # urls = get_all_urls(PATH_TO_FILE_WITH_LINKS)
    for root, dirs, files in os.walk("medications"):
        os.chdir(r"drugs")
        for file in files:
            os.chdir(r"drugs\medications")
            name, info = check_fullness(file)
            if name:
                url = info["source"]
                k = 1
                while k < 3:
                    try:
                        info['interactions'] = parse_interactions(url, driver, driver2)
                        if info['interactions']:
                            print('DONE', url, "\n\n")
                            with open(f'{name}', 'w', encoding='utf-8') as file:
                                json.dump(info, file, indent=4)
                        elif info['interactions'] is None:
                            print('NO REQUIRED', url, "\n\n")
                            with open(PATH_TO_FILE_WITH_LINKS_NO_COLLECTION, 'a', encoding='utf-8') as file:
                                file.write(f'{url}\n')
                            no_collection_required.append(url)
                        else:
                            raise NoSuchElementException
                        break
                    except Exception:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        print(url, f'ATTEMPT - {k}, Error: ', exc_type, exc_traceback)
                        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
                        time.sleep(10)
                        driver.close()
                        driver2.close()
                        driver = webdriver.Chrome(
                                desired_capabilities=caps,
                                executable_path=EXECUTABLE_PATH,
                                options=options
                            )

                        driver2 = webdriver.Chrome(
                                desired_capabilities=caps,
                                executable_path=EXECUTABLE_PATH,
                                options=options
                        )
                    k += 1
                else:
                    print(url, 'ERROR')


if __name__ == "__main__":

    agent = webdriver.Chrome(
        desired_capabilities=caps,
        executable_path=EXECUTABLE_PATH,
        options=options
    )

    agent2 = webdriver.Chrome(
        desired_capabilities=caps,
        executable_path=EXECUTABLE_PATH,
        options=options
    )

    main(agent, agent2)

    agent.close()
    agent2.close()
