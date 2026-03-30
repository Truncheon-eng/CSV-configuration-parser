import pathlib
import re

from dataclasses import dataclass
from exceptions import CollectorException
from contextlib import ExitStack
from classes import Field
from enum import Enum
from output import print_verbose, print_info

class NumberSystem(Enum):
    BIN = 0
    DEC = 1


@dataclass(init = False)
class Collector:
    
    __extension = "tv"
    __num_of_calls = 0

    """
    Класс конвертера, генерирующий выходые файлы на основе конфигурационного.
    
    :ivar __extension: расширение сохраняемого файла.
    :vartype __extension: str

    :ivar __num_of_calls: поле, необходимое для создания разных файлов с тестовыми векторами.
    :vartype __num_of_calls: int

    :ivar bottom_dump_size: нижняя граница кол-ва символов, которое необходимо считать, чтобы определить систему счисления.
    :vartype bottom_dump_size: int

    :ivar top_dump_size: верхняя граница кол-ва символов, которое необходимо считать, чтобы определить систему счисления.
    :vartype top_dump_size: int

    :ivar store_directory: директория, в которую будут сохраняться тестовые файлы.
    :vartype store_directory: pathlib.Path

    :ivar verbosity: полнота вывода для коллектора
    :vartype verbosity: bool

    :ivar dump_size: размер символов, считываемых из файлов, необходимых для определения системы счисления, исользованной в файле
    :vartype dump_size: int
    """
    bottom_dump_size = 1024
    top_dump_size = 8 * bottom_dump_size
    def __init__(self, store_directory: str, verbosity: bool, dump_size: int) -> None:
        
        self.store_directory = pathlib.Path(store_directory)
        self.verbosity = verbosity
        if self.bottom_dump_size <= dump_size <= self.top_dump_size:
            self.dump_size = dump_size
        else:
            message = (
                f"Dump size has to match constraints: "
                f"{Collector.bottom_dump_size} <= dump_size <= {Collector.top_dump_size}"
            )
            raise CollectorException(message)
        
        if not (self.store_directory.exists()):
            message = f"Directory \"{self.store_directory.absolute()}\" for storing *.{self.__extension} file doesn't exist"
            raise CollectorException(message)

        if not (self.store_directory.is_dir()):
            message = f"\"{self.store_directory.absolute()}\" for storing *.(dat|tv) file isn't a directory"
            raise CollectorException(message)
        
        return
    
    @staticmethod
    def __from_binary_to_hex(line: str, line_num: int, file_name: str, bit_len: int) -> str:
        """
        Метод from_binary_to_hex предназначен для получения из бинарных строк 
        шестнадцатиричные последовательности символов 
        
        :param line: строка, полученная из файла
        :type line: str

        :param line_num: номер рассматриваемой строки
        :type line_num: int

        :param file_name: имя файла, из которого получаем тестовое значение поля
        :type file_name: str

        :param bit_len: предполагаемое кол-во символов в строке после разделения по пробелам
        :type bit_len: int

        :return: шестнадцатиричная последовательность символов
        :rtype: str
        """
        BIN_TO_HEX_LEN = 8
        HEX_WIDTH = 4

        line_arr = line.strip().split(" ")
        
        if (len(line_arr) != bit_len):
            message = (f"Error at {line_num} string in \"{file_name.absolute()}\"."
                       f" Length of this string is not equal to {bit_len}\n"
                       f"String - \"{line.strip():.30s}\"")

            raise CollectorException(message)
        
        # if (bit_len % BIN_TO_HEX_LEN != 0):
        #     message = (f"Error at {line_num} string in \"{file_name.absolute()}\"."
        #                f" Number of expected bits ({bit_len}) at string is not divisible by {BIN_TO_HEX_LEN}\n"
        #                f"String - \"{line.strip():.30s}\"")
        #     raise CollectorException(message)

        rounded_length = bit_len + (BIN_TO_HEX_LEN - bit_len % BIN_TO_HEX_LEN)

        if (rounded_length != bit_len):
            # print_info(f"{bit_len} isn't divisible by {BIN_TO_HEX_LEN}")
            # print_info(f"interacting with {rounded_length}")
            line_arr = ["0"] * (rounded_length - bit_len) + line_arr

        result = list()
        
        for i in range(0, bit_len, BIN_TO_HEX_LEN):
            bin_ = int("".join(line_arr[i:i+BIN_TO_HEX_LEN]), 2)
            result.append(
                hex(bin_)[2:].rjust(BIN_TO_HEX_LEN // HEX_WIDTH, "0")
            )
        
        return "".join(result)
    
    @staticmethod
    def __from_dec_to_hex(line: str, line_num: int, file_name: str, inner_dimenstion: int, outer_dimension: int) -> str:
        """
        Метод from_dec_to_hex предназначен для получения из строк с десятичными числами
        шестнадцатиричные последовательности символов
        
        :param line: строка, полученная из файла
        :type line: str

        :param line_num: номер рассматриваемой строки
        :type line_num: int

        :param file_name: имя файла, из которого получаем тестовое значение поля
        :type file_name: str

        :param inner_dimension: размерность первого измерения([x:0][y:0] -> где (y - 0 + 1) - inner_dimension)
        :type inner_dimension: int

        :param outer_dimension: размерность второго измерения([x:0][y:0] -> где (x - 0 + 1) - outer_dimension)
        :type int:

        :return: шестнадцатиричная репрезентация строки десятичных символов
        :rtype: str
        """
        HEX_WIDTH = 4
        
        member_width = inner_dimenstion

        if member_width % 8 != 0:
            member_width += (8 - member_width % 8) # дополнение до кратности 8
        
        
        try:
            line_arr = [int(num) for num in line.strip().split()]
        
            if len(line_arr) != outer_dimension:
                message = (f"Error at {line_num} string in \"{file_name.absolute()}\"."
                           f"The number of words in the string expected to be equal {outer_dimension}\n"
                           f"String - \"{line.strip():.30s}\"")
                raise CollectorException(message)
            
            result = list()

            for num in line_arr:
                h = str()
                if num < 0:
                    message = (f"Error at {line_num} string in \"{file_name.absolute()}\"."
                               f"Number {num} in the string is negative\n"
                               f"String - \"{line.strip():.30s}\"")        
                    raise CollectorException(message)
                else:
                    h = hex(num)[2:]
                    
                    if len(h) > (member_width // HEX_WIDTH):
                        message = (f"Error at {line_num} string in \"{file_name.absolute()}\"."
                                   f"Number {num} in the string is too big to be stored in {member_width} bits\n"
                                   f"String - \"{line.strip():.30s}\"")
                        raise CollectorException(message)
                    
                    h = h.rjust(member_width // HEX_WIDTH, "0")
                
                result.append(h)
        
        except (ValueError, TypeError):
            message = (f"Error at {line_num} string in \"{file_name.absolute()}\"."
                       f"Got unexpected char when getting integer value from the string\n"
                       f"String - \"{line.strip():.30s}\"")
            raise CollectorException(message)


        return " ".join(result)
    
    @staticmethod
    def __from_bin_to_bin(line: str, line_num: int, file_name: str) -> str:
        """
        Метод from_bin_to_bin предназначен для получения 0 или 1 из строк с тестовыми значениями 
        
        :param line: строка, полученная из файла
        :type line: str
        
        :param line_num: номер рассматриваемой строки
        :type line_num: int

        :param file_name: имя файла, из которого получаем тестовое значение поля
        :type file_name: str

        :return: строка с 0 или 1
        :rtype: str
        """
        line = line.strip()
        if (len(line) != 1):
            message = (f"Error at {line_num} string in \"{file_name}\"."
                        f" Expected only 1 symbol at string\n"
                        f"String - \"{line:.30s}\"")
            raise CollectorException(message)
        
        return line
    
    @staticmethod 
    def __define_number_system(file_path: pathlib.Path, dump_size: int) -> NumberSystem:
        """
        Метод define_number_system предназначен для определения системы счисления файла с тестовыми векторами 

        :param file_path: путь до файла с тестовыми векторами
        :type file_path: pathlib.Path

        :param dump_size: кол-во символов, которые будут считаны для определения системы счисления
        :type dump_size: int

        :return: объект типа NumberSystem(аналог enum-а в C++)
        :rtype: NumberSystem
        """
        if not file_path.is_file():
            message = f"\"{file_path.name}\" isn't file"
            raise CollectorException(message)
        
        state = NumberSystem.BIN 

        bin = set(["0", "1"])
        dec = set(["0", "1", "2", "3", "4", "5", "6", "7", "9"])
        
        try:
            with open(file_path, "r") as file:
                dump = file.read(dump_size)
                for word in dump.split():
                    for c in word:
                        if c in bin:
                            state = NumberSystem.BIN
                            continue
                        if c in dec:
                            state = NumberSystem.DEC
                            return state
                        if c == '-' or \
                           c == 'X' or \
                           c == 'Z' or \
                           c == '_':
                            continue
                        message = f"Undefined character \"{c}\""
                        raise CollectorException(message)
        except MemoryError:
            message = (
                f"Error at {Collector.__define_number_system.__name__}\n",
                f"dump_size({dump_size} bytes) seems to be so great"
            )
            raise CollectorException(message)
        return state

    @staticmethod
    def __get_dimensions(field: Field) -> list[int]:
        """
        Метод __get_dimensions предназначен для получения всех размерностей, 
        записанных в столбце "__Implementation__" .csv конфигурационного файла 

        :param field: поле, для которого необходимо получить все размерности
        :type field: Field

        :return: список всех размерностей
        :rtype: list[int]
        """

        dimensions_width = list()

        dimension_str = field.implementation
        pattern_width = re.compile(r"\[\s*\d*\s*:\s*\d*\s*\]")
        found = pattern_width.findall(dimension_str)

        if not (len(found) > 0 and len(found) <= 2):
            message = (
                f"Error when handdling field \"{field.rtl_signal}\"\n",
                f"The number of supported dimensions can be 1 or 2\n",
                f"Got - \"{dimension_str:.30s}\""
            )
            raise CollectorException(message)

        for i in range(len(found) - 1, -1, -1):
            dimension = found[i]
            regex = r"\[\s*(\d*)\s*:\s*(\d*)\s*\]"
            pattern_digits = re.compile(regex)
            digits = pattern_digits.search(dimension).groups()

            if len(digits) != 2:
                message = (
                    f"Error when handling \"{digits}\"\n",
                    f"Expected string to match regex - \"{regex}\""
                )
                raise CollectorException(message)
            
            dimensions_width.append(
                int(digits[0]) - int(digits[1]) + 1
            )

        return dimensions_width

    def __gen_handlers(self, fields_files: dict[Field, pathlib.Path]) -> list:
        """
        Метод gen_handlers предназначен для динамического определения функции,
        необходимой для обработки определенной строки
        
        :param self: объект типа Collector
        
        :param fields_files: словарь типа Field(ключ), pathlib.Path(значение)
        :type fields_files: dict[Field, pathlib.Path] 
        
        :return: список функций, каждая из которых будет использоваться для обработки строки
        :rtype: list
        """

        handlers = list()  
        
        for field, file in fields_files.items():
            state = self.__define_number_system(file, self.dump_size)
            
            if state == NumberSystem.BIN:
                if self.verbosity:
                    message = f"\"{file.name}\" seems to be BINARY"
                    print_verbose(message)

                if field.dimension == 1:
                    handlers.append(
                        self.__from_bin_to_bin
                    )
                else:
                    handlers.append(
                        lambda line, line_num, file_name, \
                            d = field.dimension: \
                        self.__from_binary_to_hex(line, line_num, file_name, d)
                    )
            
            if state == NumberSystem.DEC:
                if self.verbosity:
                    message = f"\"{file.name}\" seems to be DECIMAL"
                    print_verbose(message)
                
                dimensions = self.__get_dimensions(field)

                handlers.append(
                    lambda line, line_num, file_name, \
                        member_width = dimensions[0], depth = dimensions[1]: \
                    self.__from_dec_to_hex(line, line_num, file_name, member_width, depth) 
                )
            
        return handlers
        
    def collect(self, fields_files: dict[Field, pathlib.Path]) -> pathlib.Path:
        """
        Метод collect предназначена для получения единообразного файла с тестовыми векторами.
        
        :param self: объект типа Collector
        :param fields_files: словарь, в котором каждому объекту типа Field сопоставляется путь до рассматриваемого файла
        :type fields_files: dict[Field, pathlib.Path]

        :return: путь до сохраненного файла
        :rtype: pathlib.Path
        """
        store_file = self.store_directory / f"vectors_{self.__num_of_calls}.{self.__extension}"

        with open(store_file, "w", buffering=1024*1024) as output_file:
            with ExitStack() as stack:

                file_wrappers = [
                    stack.enter_context(open(file, "r", buffering=1024*1024)) for file in fields_files.values()
                ]

                try:
                    handlers = self.__gen_handlers(fields_files)
                    
                    line_idx = 0
                    
                    for lines in zip(*file_wrappers, strict=True):
                        output_file.write(
                            " ".join(
                                handler(line, line_idx + 1, file_name) 
                                    for line, handler, file_name in zip(lines, handlers, fields_files.values(), strict=True)
                            ) + '\n'
                        )
                        line_idx += 1
                    
                except ValueError as e:
                    # TODO
                    # предполагается здесь увидеть исключение вызванное strict=True при создании итерируемого объекта
                    # может появиться ValueError по другой причине, поэтому надо это иметь ввиду
                    message = str(e)
                    raise CollectorException(message)
        
        self.__num_of_calls += 1
        return store_file