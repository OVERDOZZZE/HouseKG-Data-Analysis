# main.py
from parser_module.config import Config
from parser_module.parsers import *
from parser_module.utils import FileManager
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class Runner:
    def __init__(self, parser, filemanager, deal, property_type, start_page, stop_page, pattern_url):
        self.parser = parser
        self.filemanager = filemanager
        self.deal = deal
        self.property_type = property_type
        self.start_page = start_page
        self.stop_page = stop_page
        self.pattern_url = pattern_url

    def get_page_urls(self):
        return [self.pattern_url + str(url) for url in range(self.start_page, self.stop_page)]

    def collect_units_generator(self):
        urls = self.get_page_urls()
        with ThreadPoolExecutor(max_workers=10) as page_pool:
            futures = {page_pool.submit(self.parser.collect_units, url): url for url in urls}
            for future in as_completed(futures):
                page_units = future.result()
                for unit in page_units:
                    yield unit

    def run(self):
        self.parser.clean_old_cache()
        start = time.time()

        with ThreadPoolExecutor(max_workers=20) as unit_pool:
            future_to_unit = {unit_pool.submit(self.parser.parse, unit): unit for unit in self.collect_units_generator()}

            for future in as_completed(future_to_unit):
                try:
                    result = future.result()
                    self.filemanager.add(result)
                except Exception as e:
                    print(f"[Error parsing unit] {e}")

        self.filemanager.save()
        end = time.time()
        return round(end - start, 4)


class Builder:
    def __init__(self, property_type: str, start_page: int, stop_page: int, deal: str='sale', output_path: str=None):
        self.property_type = property_type
        self.start_page = start_page
        self.stop_page = stop_page
        self.deal = deal
        self.config = Config()
        self.output_path = output_path

    def build(self):
        parser_types = self.config.get_parser_types()
        parser = parser_types[self.property_type]()
        columns = ['URL'] + list(parser.config.const_target_dict.keys()) + list(parser.config.target_dict.keys())
        filemanager = FileManager(self.deal, self.property_type, columns, self.output_path)
        pattern_url = self.config.base_url + f'/{self.config.deal_types[self.deal]}-{self.config.property_types[self.property_type]}?page='

        return Runner(
            parser=parser,
            filemanager=filemanager,
            deal=self.deal,
            property_type=self.property_type,
            start_page=self.start_page,
            stop_page=self.stop_page,
            pattern_url=pattern_url
        )
