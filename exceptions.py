class ParserException(Exception):
    """
    Класс ошибки парсера. Простоя обёртка над Exception.
    
    :ivar message: сообщение об ошибке.
    :vartype __table_fields: str
    """
    
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
    

class CollectorException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ParserWarning:
    def __init__(self, curr_row_index, message, file_name):
        self.curr_row_index = curr_row_index
        self.message = message
        self.file_name = file_name

    def __str__(self):
        warning = f"Warning at {self.curr_row_index} row in \"{self.file_name}\": {self.message}"
        return warning
