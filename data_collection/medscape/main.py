import json
import os
import re
from time import sleep
from typing import List, Union

from bs4 import BeautifulSoup
from lxml.html import fromstring
from selenium import webdriver
from selenium.webdriver.common.by import By


class BioLab:
    def __init__(self, url):
        self.agent = webdriver.Firefox()
        self.agent.get(url)
        self.url = url
        self.soup = None

    def get_general_info(self) -> dict:
        mainsource = self.agent.find_element(By.XPATH, '//div[@id="maincolboxdrugdbheader"]')
        mainsource = fromstring(mainsource.get_attribute('innerHTML'))

        name = mainsource.xpath('//span[@class="drug_section_link"]/text()')
        comment = mainsource.xpath('//span[@class="drug_suffix"]/text()')
        comment = re.findall(r'\((.*?)\)', str(comment))
        other_names = mainsource.xpath('//span[@class="drugbrandname"]/text()')
        other_names1 = other_names[0].split(',')

        other_names_more = mainsource.xpath('//span[@id="drugbrandname_more"]/text()')
        if other_names_more:
            other_names2 = [x for x in other_names1 if x != " "] + other_names_more[0].split(',')
        else:
            other_names2 = [x for x in other_names1 if x != " "]

        classes = mainsource.xpath('//a[contains(@href, "https://reference.medscape.com/drugs/")]/text()')

        classes1 = []
        for cls in classes:
            if ',' in cls:
                for i in cls.split(','):
                    classes1.append(i.strip())
            else:
                classes1.append(cls.strip())

        medicine_info = {
            "name": name[0].strip().replace(comment[0], ""),
            "comment": comment[0],
            "other_names": [x.strip() for x in other_names2],
            "classes": classes1,
            "source": None,
            "pregnancy": None,
            "lactation": None
        }

        return medicine_info

    def get_pregnancy_info(self) -> dict:
        commons = self.agent.find_elements(
            By.XPATH,
            "//div[@id='content_6']/div[@class='refsection_content']/p[following-sibling::h4 or following-sibling:: h3[contains(text(),'Lactation')]]"
        )
        if not commons:
            commons = self.agent.find_elements(
                By.XPATH,
                "//div[@id='content_6']/div[@class='refsection_content']/p[following-sibling:: h3[contains(text(),'Pregnancy Categories')]]"
        )

        commons_lst = []

        for common in commons:
            common = fromstring(common.get_attribute('innerHTML'))
            common = common.text
            commons_lst.append(common)

        types = self.agent.find_elements(
            By.XPATH, "//div[@id='content_6']/div[@class='refsection_content']/h4"
        )
        types_lst = []

        for type in types:
            type = fromstring(type.get_attribute('innerHTML'))
            type = type.text
            types_lst.append(type)

        descriptions = self.agent.find_elements(
            By.XPATH,
            "//div[@id='content_6']/div[@class='refsection_content']//ul[(preceding-sibling::h4) and (following-sibling::h4 or 'Lactation')]"
        )
        descriptions_lst = []
        specifics_lst = []

        for description in descriptions:
            description = fromstring(description.get_attribute('innerHTML'))
            description = description.xpath("//li/text()")
            descriptions_lst.append(description)

        for type in types_lst:
            specifics = {
                "type": type,
                "description": descriptions_lst[int(types_lst.index(type))]
            }
            specifics_lst.append(specifics)

        pregnancy_info = {
            "common": commons_lst,
            "specific": specifics_lst
        }

        return pregnancy_info

    def get_lactation_info(self) -> dict:
        commons = self.agent.find_elements(
            By.XPATH,
            "//div[@id='content_6']/div[@class='refsection_content']/p[preceding-sibling::h3[text()='Lactation'] and following-sibling::h3[text()='Pregnancy Categories']]"
        )
        if not commons:
            commons = self.agent.find_elements(
                By.XPATH,
                "//div[@id='content_6']/div[@class='refsection_content']/p[contains(text(), 'Lactation')]"
            )

        commons_lst = []

        for common in commons:
            common = fromstring(common.get_attribute('innerHTML'))
            common = common.text
            commons_lst.append(common)

        lactation_info = {
            "common": commons_lst,
        }
        return lactation_info

    def parse_pregnancy(self):
        url = f'{self.url}'

        general = self.get_general_info()
        general["source"] = url

        url = f'{self.url}#6'
        self.agent.get(url)
        try:
            button = self.agent.find_element(
                By.XPATH,
                '//div[@class="sections-nav"]//li[contains(@class,"li_6 no_subsection")]'
            )
            button.click()

            pregnancy = self.get_pregnancy_info()
            general["pregnancy"] = pregnancy

            lactation = self.get_lactation_info()
            general["lactation"] = lactation
            return general
        except Exception:
            return general

    def get_bb_li_text(self):
        try:
            bb_lis = self.soup.find('div', class_="bbinfo").find_all('ul')
            bb_li_text = [i.find_all(string=True) for i in bb_lis]

            return bb_li_text
        except Exception:
            return []

    def get_bb_heads(self):
        try:
            bb_heads = [i.find_all(string=True) for i in self.soup.find('div', class_="bbinfo").find_all('h4')]
            return bb_heads
        except Exception:
            return []

    def get_bb_p_text(self):
        try:
            bb_p = []
            tmp = [i.find_all(string=True) for i in self.soup.find('div', class_="bbinfo").find_all('p')]
            for i in tmp:
                bb_p += i
            return bb_p
        except Exception:
            return []

    def get_cautions_indicators_text(self):
        try:
            cautions_p = []
            tmp = [i.find_all(string=True) for i in self.soup.find('h3', string='Cautions').find_next_siblings('p')]
            for i in tmp:
                cautions_p += i
        except Exception:
            cautions_p = []

        try:
            cautions_h = [i.find_all(string=True) for i in self.soup.find('h3', string='Cautions').find_next_siblings('h4')]
        except Exception:
            cautions_h = []

        try:
            cautions_li = [i.find_all(string=True) for i in self.soup.find('h3', string='Cautions').find_next_siblings('ul')]
        except Exception:
            cautions_li = []

        try:
            indicators_p = []
            tmp = [i.find_all(string=True) for i in self.soup.find('h3', string='Contraindications').find_next_siblings('p')
                   if i.find_all(string=True) not in cautions_p]
            for i in tmp:
                indicators_p += i
        except Exception:
            indicators_p = []

        try:
            indicators_h = [i.find_all(string=True) for i in
                            self.soup.find('h3', string='Contraindications').find_next_siblings('h4')
                            if i.find_all(string=True) not in cautions_h]
        except Exception:
            indicators_h = []

        try:
            indicators_li = [i.find_all(string=True) for i in
                             self.soup.find('h3', string='Cautions').find_next_siblings('ul')
                             if i.find_all(string=True) not in cautions_li]
        except Exception:
            indicators_li = []

        return cautions_p, cautions_h, cautions_li, indicators_p, indicators_h, indicators_li

    def get_specific_list(self, headers: list, lists: list):
        res = []

        for i, j in zip(headers, lists):
            j = [item for item in j if item != " "]
            res.append({'type': i[-1], 'description': j})

        return res

    def parse_warnings(self):

        self.agent.get(f'{self.url}#5')
        source = self.agent.page_source
        self.soup = BeautifulSoup(source, features='lxml')

        bb_li_text = self.get_bb_li_text()
        bb_heads = self.get_bb_heads()
        bb_p_text = self.get_bb_p_text()

        cautions_p, cautions_h, cautions_li, indicators_p, indicators_h, indicators_li = self.get_cautions_indicators_text()

        indicators_p = [i for i in indicators_p if i not in cautions_p]
        indicators_h = [i for i in indicators_h if i not in cautions_h]
        indicators_li = [i for i in indicators_li if i not in cautions_li]

        bb_spec = self.get_specific_list(bb_heads, bb_li_text)
        indicators_spec = self.get_specific_list(indicators_h, indicators_li)
        cautions_spec = self.get_specific_list(cautions_h, cautions_li)

        res = {
            'warnings': {
                'black_box_warning': {
                    'common': bb_p_text,
                    'specific': bb_spec,
                },
                'contraindicators': {
                    'common': indicators_p,
                    'specific': indicators_spec
                },
                'cautions': {
                    'common': cautions_p,
                    'specific': cautions_spec
                }
            }
        }

        return res

    def interactions_parse(self):
        self.agent.get(f'{self.url}#3')
        source = self.agent.page_source
        soup = BeautifulSoup(source, features='lxml')

        interactions = soup.find("div", id='druglistcontainer')

        interactions_list = []

        if interactions:

            for interaction in interactions.find_all("li"):
                classification = interaction.find_previous("h4").text.strip()
                if classification != "Interactions":
                    interaction_with = fromstring(str(interaction)).xpath('text()')
                    description = fromstring(str(interaction)).xpath('p/text()')

                    description = description[0] if description else ''

                    interaction_dict = {
                        "classification_type": re.findall(r'[a-zA-Z\s]+', classification)[0].strip(),
                        "interaction_with": interaction_with[0],
                        "description": {"common": description}
                    }

                    interactions_list.append(interaction_dict)

        result = {"interactions": interactions_list}

        return result

    def parse_illnesses(self):

        self.agent.get(f'{self.url}#4')
        source = self.agent.page_source
        soup = BeautifulSoup(source, features='lxml')

        illneses = soup.find('div', id='content_4')
        a = illneses.find('div', class_='refsection_content')


        list_of_li = a.find_all('li')
        list_full = []
        for i in list_of_li:
            list_full.append(i.text)
        percentages = re.findall(r'\d+[.,]?\d*(?:-\d+[.,]?\d*)?', str(list_full))

        only_ilneses = re.findall(r'[^\W\d_]+(?:\s+[^\W\d_]+)*', str(list_full))
        result = []
        for i in range(len(only_ilneses)):
            percent = percentages[i] if i < len(percentages) else None
            result.append({'name': only_ilneses[i], 'percent': percent})

        if not result:
            list_of_p = a.find_all('p')
            list_full = []

            for i in list_of_p:
                list_full.append(i.text)
            percentages = re.findall(r'\d+[.,]?\d*(?:-\d+[.,]?\d*)?', str(list_full))
            only_ilneses = re.findall(r'[^\W\d_]+(?:\s+[^\W\d_]+)*', str(list_full))
            result = []
            for i in range(len(only_ilneses)):
                percent = percentages[i] if i < len(percentages) else None
                result.append({'name': only_ilneses[i], 'percent': percent})

        return {'adverse effects': result}

    def check_not_found(self):
        try:
            elem = self.agent.find_element(by=By.XPATH, value='//div[@class="error__message-wrapper"]')
            return elem
        except Exception:
            return []

    def __del__(self):
        self.agent.close()


def save_json(data: Union[List[dict], dict], path: str):
    with open(path, 'w', encoding='utf-8') as file_result:
        json.dump(data, file_result, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    with open(r'data\links.txt', 'r', encoding='utf-8') as file:
        links = list(set([line.strip() for line in file]))
        links.sort()

    main_path = r'data'
    names = os.listdir(main_path)

    for link in links:
        try:
            drug_name = link.split('/')[-1]
            file_name = f'{drug_name.replace(":", "")}.json'

            print(file_name)

            if file_name in names:
                continue

            bio = BioLab(link)
            not_found = bio.check_not_found()
            if not_found:
                continue

            res_preg = bio.parse_pregnancy()
            res_warns = bio.parse_warnings()
            res_inters = bio.interactions_parse()
            res_ills = bio.parse_illnesses()

            res_preg.update(res_warns)
            res_preg.update(res_inters)
            res_preg.update(res_ills)

            save_json(res_preg, f'{main_path}/{file_name}')

        except Exception:
            pass

        sleep(2)
