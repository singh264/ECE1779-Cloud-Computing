from typing import List, Any


class Auction:
    def __init__(self, year: int, make: str, model: str, mileage: int, url: str):
        self.__year = year
        self.__make = make
        self.__model = model
        self.__mileage = mileage
        self.__url = url
    
    def get_auction_data(self) -> List[Any]:
        return [
            self.__year, 
            self.__make, 
            self.__model, 
            self.__mileage, 
            self.__url
        ]
    
    @staticmethod
    def get_auction_fields() -> List[str]:
        return [
            'Year',
            'Make',
            'Model',
            'Mileage',
            'Url'
        ]
