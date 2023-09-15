import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import json
from bs4 import BeautifulSoup as Bs
import openpyxl as xl


def scroll_to_xpath(agent, xpath):
    next_button = agent.find_element("xpath", xpath)
    agent.execute_script("arguments[0].scrollIntoView();", next_button)
    return next_button


def initialize(reg_num, dir_name):
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    main(driver, reg_num, dir_name)
    driver.close()
    driver.quit()


def parse(driver, isfs=0):
    root = driver.current_url
    bs = Bs(driver.page_source, 'lxml')
    table = []
    if not isfs:
        table_meta = bs.find('table', class_='ts1 qa-result-table').find_all('tr')
        headers = [i.text.strip() for i in table_meta[0].find_all('th')[1:]]
        rows = table_meta[1:]
        for i in rows:
            table.append({})
            table[-1]['Источник']: root
            code = i['onclick'].split("'")[1]
            for key, data in zip(headers, [td for td in i.find_all('td')[1:]]):
                table[-1][' '.join(key.split())] = data.text.strip()
            get_additional_info(driver, code, table)
    if isfs:
        table_meta = bs.find('table', class_='ts1').find_all('tr')
        headers = [i.text.strip() for i in table_meta[0].find_all('th')[1:]]
        rows = table_meta[1:]
        for i in rows:
            table.append({})
            table[-1]['Источник']: root
            code = i['onclick'].split("'")[1]
            for key, data in zip(headers, [td for td in i.find_all('td')[1:]]):
                table[-1][' '.join(key.split())] = data.text.strip()
            get_additional_info(driver, code, table)
    return table


def get_additional_info(driver, code, table):
    driver.get(f'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid={code}')
    sleep(.5)
    try:
        scroll_to_xpath(driver, '//tr[@id="ctl00_plate_trpackimg"]')
    except Exception:
        pass
    bs = Bs(driver.page_source, 'lxml')

    _ = bs.find_all('td', class_='ri')[-1].parent
    table[-1][_.td.text.strip('\n')] = _.find_all('td')[1].input['value']

    for add_info_table_row in bs.find_all('td', class_='tde1 tde1-additionalborder ce'):
        add_info_table_row = add_info_table_row.parent
        tb_name = add_info_table_row.find('td', class_='tde1 tde1-additionalborder ce').text.strip().replace('\n', '')
        tb_value = add_info_table_row.find('td', class_='tde2')

        try:
            if 'Международное' in tb_name:
                table[-1][' '.join(tb_name.split())] = tb_value.text.strip()

            elif 'Формы выпуска' in tb_name:
                tb = tb_value.find('tbody')
                rows_ = tb.find_all('tr', class_='hi_sys')
                # Лекарственная формаДозировкаСрок годностиУсловия хранения', 'Упаковки
                table[-1][tb_name] = []
                for hi_sys in rows_:
                    if rows_.index(hi_sys) % 2 == 0:
                        table[-1][tb_name].append({})
                        for hd, td in zip(('Лекарственная форма', 'Дозировка', 'Срок годности', 'Условия хранения'), hi_sys.find_all('td')):
                            table[-1][tb_name][-1][hd] = td.text.strip()
                    else:
                        table[-1][tb_name][-1]['Упаковки'] = [li.text.strip() for li in hi_sys.td.ul.find_all('li')]

            elif 'Сведения о стадиях' in tb_name:
                tb = tb_value.find('tbody')
                rows_ = tb.find_all('tr', class_='hi_sys')
                table[-1][tb_name] = []
                for hi_sys in rows_:
                    hd = ('Стадия производства', 'Производитель', 'Адрес производителя', 'Страна')
                    values_ = hi_sys.find_all('td')[1:]
                    table[-1][tb_name].append({
                        name_: value_.text.strip().replace(' ', ' ') for name_, value_ in zip(hd, values_)
                    })

            elif 'Нормативная' in tb_name:
                tb = tb_value.find('tbody')
                rows_ = tb.find_all('tr', class_='hi_sys')
                table[-1][tb_name] = []
                for hi_sys in rows_:
                    hd = ('Номер НД', 'Год', '№ изм', 'Наименование')
                    values_ = hi_sys.find_all('td')[1:]
                    table[-1][tb_name].append({
                        name_: value_.text.strip().replace(' ', ' ') for name_, value_ in zip(hd, values_)
                    })

            elif 'Фармако-терапевтическая' in tb_name:
                table[-1][tb_name] = tb_value.td.text.strip()

            elif 'Анатомо-терапевтическая' in tb_name:
                codes_ = tb_value.find('tr', class_='hi_sys').find_all('td')
                table[-1][tb_name] = {
                    'Код АТХ': codes_[0].text.strip(),
                    'АТХ': codes_[1].text.strip()
                }

            elif 'Фармацевтическая субстанция' in tb_name:
                tb = tb_value.find('tbody')
                rows_ = tb.find_all('tr', class_='hi_sys')
                table[-1][tb_name] = []
                for hi_sys in rows_:
                    hd = ('Международное непатентованное или группировочное или химическое наименование', 'Торг. наим.', 'Производитель', 'Адрес', 'Срок годности', 'Условия хранения', 'Фармакоп. статья / Номер НД', 'Входит в перечень нарк. средств, псих. веществ и их прекурсоров')
                    values_ = hi_sys.find_all('td')
                    table[-1][tb_name].append({
                        name_: value_.text.strip().replace(' ', ' ') for name_, value_ in zip(hd, values_)
                    })

            elif 'Особые отметки' in tb_name:
                _ = tb_value.find_all('tr')
                table[-1][tb_name] = [i.text.strip() for i in _]
        except Exception as ex:
            print(ex)
            table[-1][tb_name] = None
    table[-1]['Инструкции по применению лекарственного препарата'] = get_pdf(driver)
    return


def get_pdf(driver):
    done = True
    pdf = []
    try:
        pdf_btn = driver.find_element("xpath", '//input[@class="btn_flat_blue redir"]')
        driver.execute_script("arguments[0].scrollIntoView();", pdf_btn)
        pdf_btn.click()  # open instruction in browser
        sleep(.2)
        bs = Bs(driver.page_source, 'lxml')
        instr_blocks = json.loads(bs.find('input', {'name': 'ctl00$plate$hfInstructionModel'})['value'])['Sources']
        instr_blocks = instr_blocks
        for block in instr_blocks:
            for i_ in block['Instructions']:
                for _ in i_['Images']:
                    pdf.append('https://grls.rosminzdrav.ru/' + _['Url'].replace('\\', '/'))
    except Exception as ex:
        print(ex)
        done = False
    finally:
        return pdf if done else "Инструкция отсутствует"


def main(driver, reg_num, dir_name, isfs=0):
    root = f'https://grls.rosminzdrav.ru/GRLS.aspx?RegNumber={reg_num}&MnnR=&lf=&TradeNmR=&OwnerName=&MnfOrg=&MnfOrgCountry=&isfs={isfs}&regtype=1%2c2%2c3%2c4%2c5%2c6%2c7%2c8&pageSize=10&order=Registered&orderType=desc&pageNum=1'
    root_link = root
    driver.get(root)
    sleep(1.5)
    out = []
    try:
        out = parse(driver, isfs)
    except AttributeError:
        # if isfs == 0:
        #     main(driver, reg_num, dir_name, 1)
        # else:
        with open('log_file.txt', 'a') as f:
            f.write(f'[{reg_num}] {root}\n')
        try:
            save_json([], '[!]_'+reg_num, dir_name)
            return
        except TypeError:
            with open('log_file.txt', 'a') as f:
                f.write(f'!!!!!!!!!!!!!!!! [{reg_num}] {root}\n')
    driver.get(root)
    sleep(1.5)
    try:
        while True:
            if driver.find_element("xpath", '//td[@class="btn_flat pad_lr"]'):
                next_btn = driver.find_elements('xpath', '//td[@class="btn_flat pad_lr"]')[-1]
                if next_btn.text != '>':
                    break
            else:
                break
            next_btn.click()
            root = driver.current_url
            out += parse(driver, isfs)
            driver.get(root)
            sleep(1.5)
    except Exception as ex:
        print(ex)
        pass
    out = {
        'Регистрационный номер': reg_num,
        'Источник': root_link,
        'Препараты': out
    }
    save_json(out, reg_num, dir_name)


def save_json(data, name, dir_name):
    # with open(f'{name}.json', 'w', encoding='utf-8') as file:
    #     json.dump(data, file, ensure_ascii=False, indent=4)
    dir_name = dir_name.split('.')[0]
    name = name.replace('/', '_') if name else name   # При обратном действии для запроса нужно будет поменять на дробь обязательно
    if dir_name not in os.listdir():
        os.mkdir(dir_name)

    with open(f'{dir_name}\\{name}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    for file in os.listdir('input'):
        print(f'[{file}]')
        workbook = xl.load_workbook(os.path.join('input', file), data_only=True)
        sheet = workbook.active
        data = []
        for row in sheet.iter_rows(min_row=7):
            reg_number = row[2].value
            if not reg_number or ('.' in reg_number and ':' in reg_number):
                continue
            print(f' - {reg_number}')
            initialize(reg_number, file)
