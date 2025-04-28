# utils.py
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
import time


session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=Retry(total=5, backoff_factor=0.2))
session.mount('http://', adapter)
session.mount('https://', adapter)


class FileManager:
    def __init__(self, deal, property, columns):
        self.deal = deal
        self.property = property
        self.lock = threading.Lock()
        self.rows = []
        self.columns = columns
        self.filepath = Path().absolute() / f'{self.deal}_{self.property}.csv'

    def add(self, data: dict) -> None:
        with self.lock:
            completed_data = {col: data.get(col, '') for col in self.columns}
            self.rows.append(completed_data)
            if len(self.rows) >= 70:
                self.save()
                self.rows = []
    
    def save(self) -> None:
        df = pd.DataFrame(self.rows)
        df = df[self.columns]
        df.to_csv(
            self.filepath,
            mode='a',
            header=not self.filepath.exists(),
            index=False,
        )


class Parser(ABC):
    def collect_units(self, source: Any) -> list:
        pass
    
    def parse(self, source: Any) -> dict:
        pass
    
    def get_soup(self, response, strainer=None):
        pass
    

class BaseParser(Parser):
    def __init__(self, target_dict, config):
        self.session = session
        self.config = config
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
    
    def clean_old_cache(self, days: int = 3) -> None:
        now = time.time()
        lifetime = days * 86400  

        for file in self.cache_dir.glob('*.html'):
            if now - file.stat().st_mtime > lifetime:
                file.unlink()
