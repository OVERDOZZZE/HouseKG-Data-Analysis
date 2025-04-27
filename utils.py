import requests
from bs4 import BeautifulSoup as bs, SoupStrainer
import requests.adapters
from config import Config
import lxml
from pathlib import Path
import pandas as pd
from abc import ABC, abstractmethod
from typing import Any
from urllib3.util.retry import Retry
import threading
import hashlib
import os


session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=Retry(total=5, backoff_factor=0.2))
session.mount('http://', adapter)
session.mount('https://', adapter)


class FileManager:
    def __init__(self, deal, property):
        self.filepath = Path().absolute()
        self.deal = deal
        self.property = property
        self.lock = threading.Lock()
        self.rows = []

    def add(self, data: dict) -> None:
       with self.lock:
           self.rows.append(data)
           if len(self.rows >= 100):
               self.save()
               self.rows = ()
    
    def save(self) -> None:
        df = pd.DataFrame(self.rows)
        df.to_csv(self.filepath / f'{self.deal}_{self.property}.csv', mode='a', header=not self.filepath.exists())


class Parser(ABC):
    def collect_units(self, source: Any) -> list:
        pass
    
    def parse(self, source: Any) -> dict:
        pass
    
    def get_soup(self, response, strainer=None):
        pass
    

class BaseParser(Parser):
    def __init__(self, target_dict):
        self.session = session
        self.config = Config()
        self.target_dict = target_dict
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)

    def get_soup(self, source: str, name: str=None, attrs: dict={}):
        hash_name = hashlib.md5(source.encode()).hexdigest()
        html_path = self.cache_dir / f'{hash_name}.html'

        if html_path.exists():
            text = html_path.read_text(encoding='utf-8')
        else:
            response = self.session.get(source)
            text = response.text
            html_path.write_text(text, encoding='utf-8')

        strainer = SoupStrainer(name=name, attrs=attrs)
        soup = bs(text, 'lxml', parse_only=strainer)
        return soup
    
    def get_last_page(self, type_url) -> int:
        soup = self.get_soup(type_url, 'a', {'class': 'page-link'})
        last_page = int(soup.find_all('a', 'page-link')[-1]['data-page'])

        return last_page

    def collect_units(self, source: str) -> list:
        soup = self.get_soup(source, 'div', {'class': 'top-info'})
        divs = soup.find_all('a')
        if not divs:
            raise Exception('Empty divs')
        links = [self.config.base_url + i['href'] for i in divs]

        return links
    
    def parse_const(self, soup, targets: dict) -> dict:
        address = soup.find('div', class_='address').text
        location = [i.strip() for i in address.split(',')]
        region, city, district = 'Чуйская область', location[0], ''

        if city == 'Бишкек' and len(location) > 1:
            district = location[1]
        elif len(location) > 1:
            region = location[0]
            city = location[1]
        price = soup.find('div', class_='price-dollar').text.strip()
        name = soup.find('h1').text.strip()
        targets.update({
            'Название': name,
            'Область': region,
            'Город/Село': city,
            'Район': district,
            'Цена': price,
        })
        
        return targets

    def parse_dynamic(self, soup, targets: dict) -> dict:
        dynamic_data = soup.find_all('div', class_='info-row')

        for div in dynamic_data:
            label = div.find('div', class_='label').text.strip()
            value = div.find('div', class_='info').text.strip().replace('  ', '')
            targets[label] = value

        return targets

    def parse(self, unit: str) -> dict:
        soup = self.get_soup(unit, name='div')
        d1 = self.parse_const(soup, self.config.const_target_dict)
        d2 = self.parse_dynamic(soup, self.target_dict)

        return d1 | d2
    
    


# sector_target_dict = {
#     'Тип предложения': [],
#     'Площадь участка': [],
#     'Местоположение': [],
#     'Коммуникации': [],
#     'Разное': [],
#     'Правоустанавливающие документы': [],
#     'Возможность рассрочки': [],
#     'Возможность ипотеки': [],
#     'Возможность обмена': []
# }

# sector_target_dict = {
#     'Тип предложения': [],
#     'Дом': [],
#     'Кол-во этажей': [],
#     'Площадь': [],
#     'Площадь участка': [],
#     'Отопление': [],
#     'Состояние': [],
#     'Телефон': [],
#     'Интернет': [],
#     'Санузел': [],
#     'Канализация': [],
#     'Питьевая вода': [],
#     'Электричество': [],
#     'Газ': [],
#     'Мебель': [],
#     'Пол': [],
#     'Безопасность': [],
#     'Высота потолков': [],
#     'Правоустанавливающие документы': [],
#     'Возможность рассрочки': [],
#     'Возможность ипотеки': [],
#     'Возможность обмена': []
# }


# # Sector Parser Interface

# deal_types = {
#     'sale': 'kupit',
#     'rent': 'snyat'
# }

# property_types = {
#     'apartment': 'kvartiru',
#     'private_house': 'dom',
#     'commercial_property': 'kommercheskaia-nedvijimost',
#     'room': 'komnatu',
#     'sector': 'uchastok',
#     'country_house': 'dachu',
#     'parking_and_garage': 'parking-garaj'
# }

# deal = input(f'Select deal type: \n1.sale\n2.rent\nYour selection: ')
# property= input(f'\nSelect property type: \n1.apartment\n2.private_house\n3.sector\nYour selection: ')

# type_url = 'https://house.kg' + f'/{deal_types[deal]}-{property_types[property]}?page='


# parser = BaseParser(target_dict=sector_target_dict)

# last_page = parser.get_last_page(type_url)

# print(f'\nHere are {last_page} pages for that deal and property type! Select the range:')
# first_page = int(input('\nStart from page: '))
# last_page = int(input('\nStop on page: '))

# print(f'\nAccepted! Pages to be parsed: {last_page - first_page}\n')


# def func():
#     for page in range(first_page, last_page):
#         page_url = type_url + str(page)
#         print(page_url)
#         urls = parser.collect_units(page_url)
#         for url in urls:
#             yield parser.parse(url)

# df = pd.DataFrame()

# for row in func():
#     df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

# df.to_csv('private_houses.csv', mode='a')

