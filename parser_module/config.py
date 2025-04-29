# config.py
from enum import Enum
from pathlib import Path
import fake_useragent
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Config:
    base_url = 'https://house.kg'
    headers = {
        'User-Agent': fake_useragent.UserAgent().random,
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
        from parser_module.parsers import SectorParser, PrivateHouseParser
        return {
                'private_house': PrivateHouseParser,
                'sector': SectorParser,
            }
    
@dataclass
class SectorConfig(Config):
    target_dict = {
        'Тип предложения':'',
        'Площадь участка': '',
        'Местоположение': '',
        'Коммуникации': '',
        'Разное': '',
        'Правоустанавливающие документы': '',
        'Возможность рассрочки': '',
        'Возможность ипотеки': '',
        'Возможность обмена': ''
    }

class PrivateHouseConfig(Config):
    target_dict = {
        'Тип предложения': '',
        'Дом': '',
        'Кол-во этажей': '',
        'Площадь': '',
        'Площадь участка': '',
        'Отопление': '',
        'Состояние': '',
        'Телефон': '',
        'Интернет': '',
        'Санузел': '',
        'Канализация': '',
        'Питьевая вода': '',
        'Электричество': '',
        'Газ': '',
        'Мебель': '',
        'Пол': '',
        'Безопасность': '',
        'Высота потолков': '',
        'Правоустанавливающие документы': '',
        'Возможность рассрочки': '',
        'Возможность ипотеки': '',
        'Возможность обмена': ''
    }
