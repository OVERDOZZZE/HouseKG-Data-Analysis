import requests
from bs4 import BeautifulSoup as bs, SoupStrainer
from config import Config, SectorConfig
import lxml
from pathlib import Path
import pandas
import time


class BaseParser:
    def __init__(self, csvfile: Path, fields: list[str], data: dict[str], df: pandas.DataFrame):
        self.session = requests.Session()
        self.config = Config()
        self.fields = fields
        self.data = data
        self.df = df
        self.csvfile = self.config.main_path / csvfile
        self.headers = self.config.headers
        self.base_url = self.config.base_url
        self.session.headers.update(self.headers)


    def get_session(self):
        return self.session
    
    def collect_urls_from_page(self, page_url: str) -> list:
        response = self.session.get(page_url)
        # print(f'Conncetion response code: {response.status_code}')
        soup = bs(response.text, 'lxml', parse_only=SoupStrainer('div', class_='top-info'))
        url_list = []
        div_list = soup.find_all('a')
        # print(f'DIV LIST: {div_list}')
        if len(div_list) == 0:
            raise Exception('BANNED!')
        for div in div_list:
            url_list.append(self.base_url + div['href'])
        # print(f'Parsed page number: {page_url[-1]}')
        # print(f'Urls collected: {len(url_list)}')
        return url_list

    def parse_singe_detail_page(self, unit_url):
        response = self.session.get(unit_url)
        soup = bs(response.text, 'lxml', parse_only=SoupStrainer('div'))
        location_div = soup.find('div', class_='address')

        # Setting locations on the crooked website... :/
        if location_div is not None:
            location = [i.strip() for i in location_div.text.split(',') if i.strip()]
            # print(f'location is: {location}')
            
            if location[0] in self.config.regions:
                self.data['region'] = location[0]
                self.data['city'] = location[1]
                self.data['district'] = 'N/A'
                
            else:
                self.data['region'] = 'Чуйская область'
                self.data['city'] = location[0]

                if location[0] == 'Бишкек':
                    self.data['district'] = location[1]
                else:
                    self.data['district'] = 'N/A'
        try:
            self.data['price'] = soup.find('div', class_='price-dollar').text.strip()
        except:
            pass
        
        other_data = soup.find_all('div', class_='info-row')

        for field, data in zip(self.fields, other_data):
            value = data.find('div', class_='info').text
            label = data.find('div', class_='label').text
            if label == field:
                value = value.strip().replace('  ', '')
                self.data[field] = value     
            else:
                self.data[field] = 'null'


        self.df = pandas.DataFrame([self.data])
        self.df.to_csv(self.csvfile, mode='a', header=not self.csvfile.exists(), index=False)
        print(f'Information for {self.data["city"]} saved!')


class SectorParser(BaseParser):
    def __init__(self):
        csvfile = 'sectors.csv'
        fields = SectorConfig().get_fields()
        data = {
            'region': [],
            'city': [],
            'district': [],
            'price': [],
        }
        df = pandas.DataFrame(columns=[
            'region', 'city', 'district', 'adress', 'price', 'Тип предложения', 
            'Площадь участка', 'Местоположение', 'Коммуникации', 'Разное', 'Правоустанавливающие документы',
            'Возможность рассрочки', 'Возможность ипотеки', 'Возможность обмена'
            ])
        super().__init__(csvfile=csvfile, fields=fields, data=data, df=df)

    

parser = SectorParser()

pages_to_be_parsed = 20
page_base_url = 'https://www.house.kg/kupit-uchastok?page='


start = time.time()
for page in range(1, 4+1):
    current_page_url = page_base_url + str(page)
    urls = parser.collect_urls_from_page(current_page_url)
    print(urls)
    
    for url in urls:
        parser.parse_singe_detail_page(url)
stop = time.time()

print(f'Program executed in: {round(stop-start, 5)}')

