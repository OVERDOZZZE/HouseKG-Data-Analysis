from config import Config
from parsers import *
from utils import FileManager
from concurrent.futures import ThreadPoolExecutor
import time
import threading


class Runner:
    def __init__(self, parser, filemanager, deal, property, start_page, stop_page):
        self.parser = parser
        self.filemanager = filemanager
        self.deal = deal
        self.property = property
        self.start_page = start_page
        self.stop_page = stop_page

    def get_page_urls(self):
        return [self.pattern_url + str(url) for url in range(self.start_page, self.stop_page)]
    
    def run(self):
        urls = self.get_page_urls()
        all_units = []
        with ThreadPoolExecutor(max_workers=5) as page_pool:
            for page_units in page_pool.map(self.parser.collect_units, urls):
                all_units.extend(page_units)

        with ThreadPoolExecutor(max_workers=10) as unit_pool:
            for result in unit_pool.map(self.parser.parse, all_units):
                yield result

    def start(self):
        start = time.time()
        for row in self.run():
            self.filemanager.add(row)
        self.filemanager.save()
        end = time.time()
        print(f'Time consumed: {round(end - start, 4)} seconds')

        if self.filemanager.rows:
            self.filemanager.save()


class Builder:
    def __init__(self, property: str, start_page: int, stop_page: int, deal: str='sale'):
        self.property = property
        self.start_page = start_page
        self.stop_page = stop_page
        self.deal = deal
        self.config = Config()

    def build(self):
        parser_types = self.config.get_parser_types()
        parser = parser_types[self.property_type]()
        filemanager = FileManager(self.deal, self.property, self.parser.target_dict.keys())

        return Runner(
            parser=parser,
            filemanager=filemanager,
            deal=self.deal,
            property=self.property,
            start_page=self.start_page,
            stop_page=self.stop_page
        )
    

 
class App:
    def __init__(self, property, start_page, stop_page, deal: str='sale',):
        self.lock = threading.Lock()

    def config(self):
        self.pattern_url = self.config.pattern_url

        self.type_url = f'https://house.kg/{self.config.deal_types[self.deal]}-{self.config.property_types[self.property]}?page='
        total_pages = self.stop_page - self.start_page
        print(f'\nAccepted! Pages to be parsed: {total_pages}\nTotal URLs to be scraped: {total_pages * 10}')

        parser_type = self.config.get_parser_types()
        self.parser = parser_type[self.property]()




if __name__ == '__main__':
    app = App()
    app.setup()
    app.start()

