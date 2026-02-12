import csv
from exceptions import ParserException
from output import print_warning

class Field:
    """
    Класс поля. Пример поля (в .csv файле):
        - [127:0],128,0x00,-,DATA,DATA_IN,DATA_IN, где
        - [127:0] - значение __Implementation__
        - 128 - значение __Dimension__
        - 0x00 - значение __TV_Offset__
        - "-" - значение __Bit_Position
        - "DATA" - значение __RTL_Signal__
        - "DATA_IN" - значение __Model_Signal__
        - "DATA_IN" - значение __Doc_Signal__
    
    :ivar __table_fields: Список названий полей соотв. ячеек.
    :vartype __table_fields: list[str]
    """
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
    """
    Класс представляет информацию о полях и файлах, ассоциированных с ними.
    
    :ivar fields: массив полей, найденных на этапе поиска входных/выходных векторов.
    :vartype fields: list[Field]

    :ivar marker: строка, обычно представляющее собой одно из двух возможных значений ("INPUTS" или "OUTPUTS")
    :vartype marker: str
    """
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
                result.append(f"{self.marker}; {key} - file \"{value}\"")
                with_files += 1
            else:
                without_files.append(str(key))
            total += 1

        result.append(f"{self.marker}; Number of fields with files - {with_files}; Total number of fields - {total}")
        if len(without_files) != 0:
            result.append(f"{self.marker}: Fields without files - {', '.join(without_files)}")
        return "\n".join(result)


class InOutFields:
    """
    Класс множества полей определенной структуры (либо Inputs, либо Outputs)
    
    :ivar marker: тип векторов (само значение берется из первой ячейки строчек типа: "INPUTS,Total_Bits_In,136,Total_Bytes_In,17,,").
    :vartype __table_fields: str

    :ivar total_bits: общее кол-во битов (входных / выходных)
    :vartype total_bits: int

    :ivar total_bytes: общее кол-во байтов (входных / выходных)
    :vartype total_bits: int

    :ivar fields: поля, записанные в .csv файле (входные / выходные)
    :vartype fields: list[Field]
    """
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
    """
    Класс метаинформации модуля, содержит в себе информацию о модуле, ID модуля.
    
    :ivar module: название модуля.
    :vartype module: str

    :ivar module_id: ID модуля.
    :vartype module_id: int
    """
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
    """
    Класс потока ввода с буферизацией.
    
    :ivar __num_of_cells: кол-во ячеек, которое должно находится в кадой строке.
    :vartype __num_of_cells: str

    :ivar file: файл, с которым ассоциирован буфер.
    :vartype file: io.TextIOWrapper

    :ivar last_line: последняя, сохраненная в буфер строка.
    :vartype last_line: str

    :ivar is_waiting: флаг, определяющий заполненность буфера (True - заполнен, False - пустой).
    :vartype last_line: bool
    """
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