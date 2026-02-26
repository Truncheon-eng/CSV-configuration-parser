class ParserException(Exception):
    """
    Класс ошибки парсера. Простоя обёртка над Exception.
    
    :ivar message: сообщение об ошибке.
    :vartype message: str
    """
    
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
    

class CollectorException(Exception):
    """
    Класс ошибки коллектора. Простоя обёртка над Exception.
    
    :ivar message: сообщение об ошибке.
    :vartype message: str
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message