# main.py
from config import Config
from parsers import *
from utils import FileManager
from concurrent.futures import ThreadPoolExecutor
import time


class Runner:
    def __init__(self, parser, filemanager, deal, property, start_page, stop_page, pattern_url):
        self.parser = parser
        self.filemanager = filemanager
        self.deal = deal
        self.property = property
        self.start_page = start_page
        self.stop_page = stop_page
        self.pattern_url = pattern_url  

    def get_page_urls(self):
        return [self.pattern_url + str(url) for url in range(self.start_page, self.stop_page)]
    
    def collect_units(self):
        urls = self.get_page_urls()
        units = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for page_units in executor.map(self.parser.collect_units, urls):
                units.extend(page_units)
        return units

    def run(self):
        self.parser.clean_old_cache() 
        start = time.time()
        units = self.collect_units()
        with ThreadPoolExecutor(max_workers=10) as unit_pool:
            for result in unit_pool.map(self.parser.parse, units):
                self.filemanager.add(result)
        self.filemanager.save()
        end = time.time()
        return round(end - start, 4)
    
    
class Builder:
    def __init__(self, property: str, start_page: int, stop_page: int, deal: str='sale'):
        self.property = property
        self.start_page = start_page
        self.stop_page = stop_page
        self.deal = deal
        self.config = Config()

    def build(self):
        parser_types = self.config.get_parser_types()
        parser = parser_types[self.property]()
        columns = ['URL'] + list(parser.config.const_target_dict.keys()) + list(parser.config.target_dict.keys())
        filemanager = FileManager(self.deal, self.property, columns)
        pattern_url = self.config.base_url + f'/{self.config.deal_types[self.deal]}-{self.config.property_types[self.property]}?page='

        return Runner(
            parser=parser,
            filemanager=filemanager,
            deal=self.deal,
            property=self.property,
            start_page=self.start_page,
            stop_page=self.stop_page,
            pattern_url=pattern_url 
        )
    
