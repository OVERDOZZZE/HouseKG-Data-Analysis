from enum import Enum
from pathlib import Path


class Config:
    base_url = 'https://house.kg'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.94 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'connection': 'keep-alive',
        'accept-encoding': 'gzip, deflate',
        'host': 'www.house.kg',
        'Referer': 'https://house.kg'
    }
    main_path = Path().absolute()

    const_target_dict = {
        'Название': [],
        'Область': [],
        'Город/Село': [],
        'Район': [],
        'Цена': [],
    }

    deal_types = {
    'sale': 'kupit',
    'rent': 'snyat'
    }

    property_types = {
        'apartment': 'kvartiru',
        'private_house': 'dom',
        'commercial_property': 'kommercheskaia-nedvijimost',
        'room': 'komnatu',
        'sector': 'uchastok',
        'country_house': 'dachu',
        'parking_and_garage': 'parking-garaj'
    }
    
    @staticmethod
    def get_parser_types():
        from parsers import SectorParser, PrivateHouseParser
        return {
                # 'apartment': ApartmentParser,
                'private_house': PrivateHouseParser,
                # 'commercial_property': CommercialPropertyParser,
                # 'room': RoomParser,
                'sector': SectorParser,
                # 'country_house': CountryHouseParser,
                # 'parking_and_garage': ParkingGarageParser
            }



class SectorConfig(Config):
    target_dict = {
        'Тип предложения': [],
        'Площадь участка': [],
        'Местоположение': [],
        'Коммуникации': [],
        'Разное': [],
        'Правоустанавливающие документы': [],
        'Возможность рассрочки': [],
        'Возможность ипотеки': [],
        'Возможность обмена': []
    }

class PrivateHouseConfig(Config):
    target_dict = {
        'Тип предложения': [],
        'Дом': [],
        'Кол-во этажей': [],
        'Площадь': [],
        'Площадь участка': [],
        'Отопление': [],
        'Состояние': [],
        'Телефон': [],
        'Интернет': [],
        'Санузел': [],
        'Канализация': [],
        'Питьевая вода': [],
        'Электричество': [],
        'Газ': [],
        'Мебель': [],
        'Пол': [],
        'Безопасность': [],
        'Высота потолков': [],
        'Правоустанавливающие документы': [],
        'Возможность рассрочки': [],
        'Возможность ипотеки': [],
        'Возможность обмена': []
    }


class ContractType(Enum):
    SALE = 'kupit'
    RENT = 'snyat'


class RealEstateType(Enum):
    SECTOR = 'uchastok'

