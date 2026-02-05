class FieldException(Exception):
    def __init__(self, expected_list, real_list):
        self.expected_list = expected_list
        self.real_list = real_list

    def __str__(self):
        return f"\nExpected: {self.expected_list}\n" + f"Received instead: {self.real_list}"


class ParserException(Exception):
    __marker = "[x]"
    def __init__(self, message):
        self.message = message

    def __str__(self):
        error_result = list()
        for seq in self.message.split("\n"):
            error_result.append(f"{self.__marker} {seq}")
        return "\n".join(error_result) 


class ParserWarning:
    def __init__(self, curr_row_index, message, file_name):
        self.curr_row_index = curr_row_index
        self.message = message
        self.file_name = file_name

    def __str__(self):
        warning = f"Warning at {self.curr_row_index} row in \"{self.file_name}\": {self.message}"
        return warning
