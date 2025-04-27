from config import Config
from parsers import *
from utils import FileManager
from concurrent.futures import ThreadPoolExecutor
import time
import threading
from multiprocessing import cpu_count


class App:
    def __init__(self):
        self.config = Config()
        self.deal = 'sale'
        self.property = input('Property type: ')
        self.start_page = int(input('Start Page: '))
        self.stop_page = int(input('Stop Page: '))
        self.parser = None
        self.lock = threading.Lock()
        self.filemanager = FileManager(self.deal, self.property)

    def setup(self) -> None:
        self.type_url = f'https://house.kg/{self.config.deal_types[self.deal]}-{self.config.property_types[self.property]}?page='
        print(f'\nAccepted! Pages to be parsed: {self.stop_page - self.start_page}\n')

        parser_type = self.config.get_parser_types()
        self.parser = parser_type[self.property]()

    def get_page_urls(self):
        return [self.type_url + str(url) for url in range(self.start_page, self.stop_page)]

    def run(self):
        urls = self.get_page_urls()

        # 1. First collect all unit URLs
        all_units = []
        with ThreadPoolExecutor(max_workers=5) as page_pool:
            for page_units in page_pool.map(self.parser.collect_units, urls):
                all_units.extend(page_units)

        # 2. Then parse all units
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


if __name__ == '__main__':
    app = App()
    app.setup()
    app.start()

