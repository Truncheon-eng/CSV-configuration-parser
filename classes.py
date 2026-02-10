import csv
from exceptions import ParserException
from output import print_warning

class Field:
    # TODO: по запросу расширить кол-во необходимых полей
    def __init__(self, field_name, implementation, dimension):
        self.field_name = field_name
        self.implementation = implementation
        # try:
        self.dimension = dimension
        # except ValueError:
            # message = f"Error when getting integer value from __Dimension__: \"{dimension}\""
            # raise ParserException(message)
    
    def __str__(self):
        result = (f"Field name: {self.field_name}, "
                  f"Implementation: {'None' if self.implementation == '' else self.implementation}, "
                  f"Dimension: {self.dimension};")
        return result

class FieldValidator:
    def __init__(self, fields: list, marker: str):
        self.fields_files = dict()
        for field in fields:
            self.fields_files[field.field_name] = None
        self.marker = marker

    def __str__(self):
        result = list()
        total = 0
        with_files = 0
        without_files = list()

        for key, value in self.fields_files.items():
            if not value is None:
                result.append(f"{self.marker}: {key} - file \"{value}\"")
                with_files += 1
            else:
                without_files.append(str(key))
            total += 1

        result.append(f"{self.marker}: Number of fields with files - {with_files}; Total number of fields - {total}")
        if len(without_files) != 0:
            result.append(f"{self.marker}: Fields without files - {', '.join(without_files)}")
        return "\n".join(result)


class InOutFields:
    def __init__(
            self, 
            marker: str, 
            total_bits: str, 
            total_bytes: str,
            fields: list[Field]
        ):
        self.marker = marker
        try:
            self.total_bits = int(total_bits)
        except (ValueError, TypeError):
            message = f"\"{total_bits}\" in Total_Bits_... can't be interpreted as integer value, when reading {InOutFields.__name__}"
            raise ParserException(message)
        
        try:
            self.total_bytes = int(total_bytes)
        except (ValueError, TypeError):
            message = f"\"{total_bytes}\" in Total_Bytes_... can't be interpreted as integer value, when reading {InOutFields.__name__}"
            raise ParserException(message)

        self.fields = fields
        
class ModuleInfo:

    def __init__(self, module: str, module_id: str):
        # TODO: насколько помню не везде присутствует __Subsystems__
        # TODO: насколько целесообразно тогда добавлять эти поля
        self.module = module
        try:
            self.module_id = int(module_id)
        except (TypeError, ValueError):
            message = f"\"{module_id}\" value can't be interpreted as integer, when reading {ModuleInfo.__name__}"
            print_warning(message)
            self.module_id = None
    
    
    def __str__(self):
        message = f"Module: {self.module}\n"
        message += f"Module ID: {self.module_id}"
        return message


class BufferStream:

    __num_of_cells = 7
    def __init__(self, file):
        self.file = file
        self.last_line = None
        self.is_waiting = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.is_waiting:
            self.is_waiting = False
            return self.last_line
        if self.eof():
            raise StopIteration
        
        self.last_line = self.file.readline()
        
        csv_reader = csv.reader([self.last_line])

        if len(next(csv_reader)) != self.__num_of_cells:
            message = f"\"{self.last_line.strip()}\" doesn't contain {self.__num_of_cells} cells"
            raise ParserException(message)

        return self.last_line

    def step_back(self) -> None:
        """
        Метод step_back выставляет поле is_waiting в True, чтобы следующее считывание, происходило из последней
        считанной строки
        
        :param self: объект класса BufferStream
        """
        if self.is_waiting:
            message = f"Double call of {BufferStream.step_back.__name__} in {BufferStream.__name__}"
            raise ParserException(message)
        self.is_waiting = True
        return
    

    def eof(self) -> bool:
        """
        Метод eof предназначен дял определения конца файла.
        
        :param self: объект типа BufferStream
        :return: конец файла (True / False)
        :rtype: bool
        """
        symbol = self.file.read(1)
        
        if symbol:
            self.file.seek(self.file.tell() - 1)
            return False
        
        if self.is_waiting:
            return False

        return True