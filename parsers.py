from utils import BaseParser
from config import SectorConfig, PrivateHouseConfig

class SectorParser(BaseParser):
    def __init__(self):
        self.config = SectorConfig()
        target_dict = self.config.target_dict

        super().__init__(target_dict=target_dict)

    def run(self):
        pass
    

class PrivateHouseParser(BaseParser):
    def __init__(self):
        self.config = PrivateHouseConfig
        target_dict = self.config.target_dict

        super().__init__(target_dict=target_dict)

    def run(self):
        pass
    