class Worker:
    def __init__(self, id: str, state: str, name: str = 'Unknown') -> None:
        self.__id = id
        self.__state = state
        self.__name = name
    
    @property
    def id(self) -> str:
        return self.__id
    
    @property
    def state(self) -> str:
        return self.__state
    
    @property
    def name(self) -> str:
        return self.__name
    
    def __str__(self) -> str:
        return f'({self.id}, {self.state}, {self.name})'

    def __repr__(self) -> str:
        return self.__str__()
