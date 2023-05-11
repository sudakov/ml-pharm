import html
import io
import json
import os
import re
import time

import pandas as pd
from lxml.etree import ParserError
from lxml.html import fromstring, tostring
from selenium import webdriver
from selenium.webdriver.common.by import By


def get_text_by_xpath(driver, xpath: str):
    element = driver.find_element(by=By.XPATH, value=xpath)
    if element:
        return element.text

    return None


def clean_text(text):
    return " ".join(text.split()).replace('\xa0', '')


class ParseMainInfo:

    def __init__(self, main_block):
        self.main_block = main_block

    def _get_key_name(self, value):
        if 'Кодирование по Международной статистической' in value:
            return 'classification'
        if 'Год утверждения' in value:
            return 'approval_year'
        if 'Возрастная категория' in value:
            return 'age_category'
        if 'Пересмотр не позднее'in value:
            return 'revision_no_later'
        if 'Разработчик клинической рекомендации' in value:
            return 'clinical_guideline_developers'
        if 'ID' in value:
            return 'id'
        return None

    def parse(self):
        result = {}

        for info in self.main_block.xpath('//div[contains(@class, "main-dopinfo")]'):
            info_block = fromstring(tostring(info))
            for item in info_block.xpath('//div/div'):
                item_block = fromstring(tostring(item))
                key_name = self._get_key_name(" ".join(item_block.xpath('//span/text()')))
                if key_name == 'clinical_guideline_developers':
                    result[key_name] = item_block.xpath('//li/text()')
                elif key_name == 'classification':
                    classifications = re.findall(
                        r'\w\d{1,4}.\d{1,3}', item_block.xpath('//b/text()')[0]
                    )
                    if not classifications:
                        classifications = item_block.xpath('//b/text()')[0].split(', ')
                    result[key_name] = classifications
                elif key_name:
                    result[key_name] = item_block.xpath('//b/text()')[0]

        return result


class ParseUnit:

    @staticmethod
    def _html_table_to_csv(table):
        # result = []

        # for row in table.xpath('//tr'):
        #     row_html = fromstring(tostring(row))
        #     result.append([clean_text(cell.text_content()) for cell in row_html.xpath('//td')])

        # return result
        str_table = tostring(table).decode("utf-8").replace('\n', '')
        str_table = re.sub(r'(\d+)(,)(\d+)', r'\1.\3', str_table)
        html_table = pd.read_html(str_table)

        s_buf = io.StringIO()
        html_table[0].to_csv(s_buf, index=False)

        str_table = s_buf.getvalue().split('\n')

        if all(item.isdigit() for item in str_table[0].split(',')):
            str_table = str_table[1:]

        return str_table

    def parse(self, blocks, wanted_tag):
        text = [blocks[0]]
        tables = []

        is_nested = False
        sub_chapters = []
        chapters = []
        name = blocks[0] if isinstance(blocks[0], str) else clean_text(blocks[0].text_content())
        for item in blocks[1:]:
            tag_name = item.xpath('name()') if not isinstance(item, str) else ''

            if is_nested:
                if tag_name == wanted_tag:
                    if sub_chapters:
                        chapters.append(sub_chapters)
                    sub_chapters = [item]
                else:
                    sub_chapters.append(item)
            else:
                if tag_name == 'table':
                    table_name = text[-1] if text else None
                    tables.append({
                        'name': table_name if isinstance(table_name, str) else table_name.text if table_name is not None else None,
                        'html': html.unescape(tostring(item).decode("cp1255").replace('\n', '')),
                        'csv': self._html_table_to_csv(item)
                    })
                    if table_name:
                        text = text[:len(text)-1]
                elif tag_name == wanted_tag:
                    sub_chapters.append(item)
                    is_nested = True
                else:
                    raw_text = item if isinstance(item, str) else item.text_content()
                    text.append(clean_text(raw_text))

        if is_nested and sub_chapters is not None:
            chapters.append(sub_chapters)

        nested_objects = []
        if wanted_tag == 'h2':
            nested_objects = [self.parse(item, '') for item in chapters]

        result = {
            'name': name,
            'text': "\n".join(text[1:])
        }

        if name == 'Список литературы':
            result['text'] = result['text'].split('\n')

        if tables:
            result['tables'] = tables
        if nested_objects:
            result['nested_objects'] = nested_objects

        return result


def get_page_data(url: str):
    result = {}

    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(2)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    result['name'] = get_text_by_xpath(driver, '//h1[@class="green-color"]')
    result['url'] = link

    main_block = fromstring(
        driver.find_element(
            by=By.XPATH,
            value='//div[@class="main-text"]'
        ).get_attribute('innerHTML')
    )
    main_block = ParseMainInfo(main_block).parse()
    result.update(main_block)

    result['content'] = [
        item.text for item in driver.find_elements(
            by=By.XPATH, value='//ul[contains(@class, "menu")]/li/a'
        )
    ]
    result['full_text'] = []

    for item in driver.find_elements(
        by=By.XPATH, value='//h1[contains(@id, "doc")]/following-sibling::div'
    ):
        try:
            html_block = fromstring(item.get_attribute('innerHTML'))
            content_blocks = [
                item.find_element(by=By.XPATH, value='preceding-sibling::h1').text
            ] + html_block.xpath('//div/*')
            value = ParseUnit().parse(content_blocks, 'h2')
        except ParserError:
            value = []

        result['full_text'].append(value)

    driver.close()

    return result


if __name__ == '__main__':
    FILE_WITH_IDENTIFICATIONS = 'data/identifications.txt'
    DATA_FOLDER = 'data'
    URL_CORE = 'https://cr.minzdrav.gov.ru/schema/'

    collected = os.listdir(DATA_FOLDER)
    with open(FILE_WITH_IDENTIFICATIONS, 'r', encoding='utf-8') as file:
        identifications = file.readlines()
        for page_id in identifications:
            page_id = page_id.replace('\n', '')

            if f'{page_id}.json' in collected:
                print('COLLECTED', page_id)
                continue

            link = f'{URL_CORE}{page_id}'
            data = get_page_data(link)
            with open(os.path.join(DATA_FOLDER, f'{page_id}.json'), 'w', encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                print('SAVED', page_id)
