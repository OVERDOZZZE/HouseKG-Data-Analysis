# parsers.py
from utils import BaseParser
from config import SectorConfig, PrivateHouseConfig

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
    