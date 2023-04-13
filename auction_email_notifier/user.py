class User:
    def __init__(self, name: str, email: str) -> None:
        self.__name = name
        self.__email = email

    @property
    def name(self) -> str:
        return self.__name

    @property
    def email(self) -> str:
        return self.__email
