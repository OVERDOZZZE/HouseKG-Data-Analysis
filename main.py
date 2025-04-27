from config import Config
from parsers import *
from utils import FileManager


class App:
    def __init__(self):
        self.config = Config()
        self.deal = 'sale'
        self.property = input('Property type: ')
        self.start_page = int(input('Start Page: '))
        self.stop_page = int(input('Stop Page: '))
        self.parser = None
        self.filemanager = FileManager(self.deal, self.property)

    def setup(self) -> None:
        self.type_url = f'https://house.kg/{self.config.deal_types[self.deal]}-{self.config.property_types[self.property]}?page='
        print(f'\nAccepted! Pages to be parsed: {self.stop_page - self.start_page}\n')

        parser_type = self.config.get_parser_types()
        self.parser = parser_type[self.property]()

    def run(self):
        for page in range(self.start_page, self.stop_page):
            page_url = self.type_url + str(page)
            urls = self.parser.collect_units(page_url)

            for url in urls:
                yield self.parser.parse(url)

    def start(self):
        for row in self.run():
            self.filemanager.add(row)
        self.filemanager.save()



if __name__ == '__main__':
    app = App()
    app.setup()
    app.start()

