# parsers.py
from parser_module.utils import BaseParser
from parser_module.config import SectorConfig, PrivateHouseConfig, ApartmentConfig

class SectorParser(BaseParser):
    def __init__(self):
        config = SectorConfig()
        super().__init__(target_dict=config.target_dict, config=config)

    def run(self):
        pass
    

class PrivateHouseParser(BaseParser):
    def __init__(self):
        config = PrivateHouseConfig()
        super().__init__(target_dict=config.target_dict, config=config)

    def run(self):
        pass


class ApartmentParser(BaseParser):
    def __init__(self):
        config = ApartmentConfig()
        super().__init__(target_dict=config.target_dict, config=config)

    def run(self):
        pass
    