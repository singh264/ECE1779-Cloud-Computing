from datetime import datetime

class GraphData:
    def __init__(self, timestamp: datetime, value: float) -> None:
        self.__timestamp = timestamp
        self.__value = value
    
    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def value(self) -> float:
        return self.__value

    def __str__(self) -> str:
        return f'({self.timestamp}, {self.value})'

    def __repr__(self) -> str:
        return self.__str__()
