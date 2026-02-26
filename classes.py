import csv
from exceptions import ParserException
from output import print_warning
from dataclasses import dataclass
import pathlib

@dataclass(frozen=True) # декоратор, который объявляет, что любой инстанс Field - неизменяемый объект
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
    
    :ivar rtl_signal: содержимое ячейки столбца "__RTL_Signal__".
    :vartype rtl_signal: str

    :ivar model_signal: содержимое ячейки столбца "__Model_Signal__".
    :vartype model_signal: str

    :ivar implementation: содержимое ячейки столбца "implementation".    
    :vartype implementation: int

    :ivar simulating: идентификатор, показывающий является ли поле симулируемым или же регистровым.    
    :vartype simulating: bool

    :ivar dimension: кол-во бит, занимамемых данным полем в тестовых векторах.    
    :vartype dimension: int

    """
    # TODO: поменять описание
    # TODO: по запросу расширить кол-во необходимых полей

    rtl_signal: str
    model_signal: str
    implementation: str
    simulating: bool
    dimension: int

    def __str__(self):
        # TODO: при изменение параметров объекта менять метод __str__
        result = (f"{{\n\t.rtl_signal = \"{self.rtl_signal}\",\n"
                 f"\t.model_signal = \"{self.model_signal}\",\n"
                 f"\t.simulating = \"{self.simulating}\"\n"
                 f"\t.implementation = \"{self.implementation}\",\n"
                 f"\t.dimension = \"{self.dimension}\"\n}}")
        return result

class FieldValidator:
    """
    Класс представляет информацию о полях и файлах, ассоциированных с ними.

    :ivar total_fields: общее кол-во всех полей.
    :vartype total_fields: int 

    :ivar num_with_files: кол-во полей, ассоциированных с файлыми тестовых векторов.
    :vartype num_with_files: int
    
    :ivar rtls_without_files: множество файлов, неассоциированных с какими-либо файлами.
    :vartype rtls_without_files: set

    :ivar fields_files: словарь полей и файлов путей до файлов, ассоциируемых с ними.
    :vartype fields_files: dict[field, pathlib.Path]

    :ivar marker:  маркер типа полей ("INPUTS/OUTPUTS")
    :vartype marker: str
    """
    def __init__(self, fields: list, marker: str):
        self.total_fields = len(fields)
        self.num_with_files = 0
        self.rtls_without_files = set([field.rtl_signal for field in fields])
        self.fields_files = dict()
        self.marker = marker


    def associate_with_file(self, field: Field, file_name: pathlib.Path) -> None:
        """
        Метод associate_with_file предназначен для взаимодействия с полем self.fields_files.
        Public интерфейс для ассоциации файла с полем
        
        :param self: объект класса Collector
        
        :param field: поле, которое необходимо ассоциировать с файлом
        :type field: Field 
        
        :param file_name: путь до файла с тестовыми векторами
        :type file_name: path.Pathlib
        
        :rtype: None
        """
        if not field in self.fields_files:
            self.fields_files[field] = file_name
            self.rtls_without_files.discard(field.rtl_signal)
        else:
            message = (f"Except file \"{self.fields_files[field].name}\" "
                f"field \"{field.rtl_signal}\" also matches the file \"{file_name.name}\"")
            print_warning(message)
        return


    def check_field(self, field: Field) -> bool:
        """
        Метод check_field проверяет, есть ли для поля файл, ассоциированный с ним
        
        :param field: поле, для которого необходимо сделать проверку
        :type field: Field
        
        :rtype: bool
        """
        return field in self.fields_files
    
    def __str__(self):
        result = list()

        for key, value in self.fields_files.items():
            result.append(f"{self.marker}; \"{key.rtl_signal}\" - file \"{value.name}\"")
            self.num_with_files += 1

        result.append(f"{self.marker}; "
                      f"Number of fields with files - {self.num_with_files}; "
                      f"Total number of fields - {self.total_fields}")
        if len(self.rtls_without_files) != 0:
            result.append(f"{self.marker}; Fields without files - {', '.join(self.rtls_without_files)}")
        
        return "\n".join(result)


class InOutFields:
    """
    Класс множества полей определенной структуры (либо Inputs, либо Outputs)
    
    :ivar marker: тип векторов (само значение берется из первой ячейки строчек типа: "INPUTS,Total_Bits_In,136,Total_Bytes_In,17,,").
    :vartype marker: int

    :ivar total_bits: общее кол-во битов (входных / выходных)
    :vartype total_bits: int

    :ivar total_bytes: общее кол-во байтов (входных / выходных)
    :vartype total_bytes: int

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
    Класс метаинформации модуля.
    Содержит в себе информацию о модуле, ID модуля.
    
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
    __num_of_cells = 8
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