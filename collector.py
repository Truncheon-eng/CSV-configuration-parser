import pathlib
import re

from dataclasses import dataclass
from exceptions import CollectorException
from contextlib import ExitStack
from classes import Field
from enum import Enum
from output import print_info

class NumberSystem(Enum):
    BIN = 0
    DEC = 1


# TODO: не забыть сделать невызываемые методы из Collector-а вызываемыми, например статические методы 

@dataclass(init = False)
class Collector:
    
    __extension = "tv"
    __num_of_calls = 0

    """
    Класс конвертера, генерирующий выходые файлы на основе конфигурационного.
    
    :ivar __extension: расширение сохраняемого файла.
    :vartype __num_of_cells: str

    :ivar __num_of_calls: поле, необходимое для создания разных файлов с тестовыми векторами.
    :vartype file: int

    :ivar store_directory: директория, в которую будут сохраняться тестовые файлы.
    :vartype last_line: pathlib.Path
    """

    def __init__(self, store_directory: str) -> None:
        self.store_directory = pathlib.Path(store_directory)

        if not (self.store_directory.exists()):
            message = f"Directory \"{self.store_directory.absolute()}\" for storing *.{self.__extension} file doesn't exist"
            raise CollectorException(message)

        if not (self.store_directory.is_dir()):
            message = f"\"{self.store_directory.absolute()}\" for storing *.(dat|tv) file isn't a directory"
            raise CollectorException(message)
        
        return
    
    @staticmethod
    def from_binary_to_hex(line: str, line_num: int, file_name: str, bit_len: int) -> str:
        """
        Метод from_binary_to_hex предназначен для получения из бинарных строк 
        шестнадцатиричные последовательности символов 
        
        :param line: строка, полученная из файла
        :param line_num: номер рассматриваемой строки
        :param bit_len: предполагаемое кол-во символов в строке после разделения по пробелам

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
        
        if (bit_len % BIN_TO_HEX_LEN != 0):
            message = (f"Error at {line_num} string in \"{file_name.absolute()}\"."
                       f" Number of expected bits ({bit_len}) at string is not divisible by {BIN_TO_HEX_LEN}\n"
                       f"String - \"{line.strip():.30s}\"")
            raise CollectorException(message)

        result = list()
        
        for i in range(0, bit_len, BIN_TO_HEX_LEN):
            bin_ = int("".join(line_arr[i:i+BIN_TO_HEX_LEN]), 2)
            result.append(
                hex(bin_)[2:].rjust(BIN_TO_HEX_LEN // HEX_WIDTH, "0")
            )
        
        return "".join(result)
    
    @staticmethod
    def from_dec_to_hex(line: str, line_num: int, file_name: str, member_width: int, depth: int) -> str:
        # TODO: начать использовать line_num для указания на строку, в которой возникло исключение
        # TODO: на отрицательные числа генерировать исключения
        # TODO: на X в последовательности символов нужно также генерировать исключение

        HEX_WIDTH = 4

        if member_width % 8 != 0:
            member_width += (8 - member_width % 8) # дополнение до 8
        
        # TODO: убрать вообще assert
        assert(member_width % 8 == 0)
        
        # TODO: проверить наличие исключения здесь
        line = [int(num) for num in line.strip().split()]
        
        # TODO: добавить исключение вместо assert
        assert(len(line) == depth)
        result = list()

        for num in line:
            h = str()
            if num == -1:
                # TODO: понять, что необходимо сделать с отрицательным числом
                h = "f" * (member_width // HEX_WIDTH)
            else:
                h = hex(num)[2:]
                # TODO: заменить assert на важный exception
                assert(len(h) <= (member_width // HEX_WIDTH))
                h = h.rjust(member_width // HEX_WIDTH, "0")
            
            result.append(h)

        # TODO: не забыть удалить assert
        assert(len("".join(result)) == (member_width // HEX_WIDTH) * depth)
        return "".join(result)
    
    @staticmethod
    def from_bin_to_bin(line: str, line_num: int, file_name: str) -> str:
        """
        Метод from_bin_to_bin 0 или 1 из строки с 0 или 1 
        
        :param line: строка, полученная из файла
        :param line_num: номер рассматриваемой строки

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
    def define_number_system(file_path: pathlib.Path, dump_size: int) -> NumberSystem:
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
                        #TODO: обработать X
                        if c == '-':
                            continue
                        message = f"Undefined character \"{c}\""
                        raise CollectorException(message)
        except MemoryError:
            message = (
                f"Error at {Collector.define_number_system.__name__}\n",
                f"dump_size({dump_size} bytes) seems to be so great"
            )
            raise CollectorException(message)
        return state

    @staticmethod
    def __get_implementation(dimension_str: str) -> list[int]:
        imps = list()

        pattern_width = re.compile(r"\[\s*\d*\s*:\s*\d*\s*\]")
        found = pattern_width.findall(dimension_str)

        # TODO: заменить assert        
        assert(len(found) > 0 and len(found) <= 2)

        for imp in found:
            pattern_digits = re.compile(r"\[\s*(\d*)\s*:\s*(\d*)\s*\]")
            digit_groups = pattern_digits.search(imp).groups()
            
            assert(len(digit_groups) == 2)

            imps.append(
                int(digit_groups[0]) - int(digit_groups[1]) + 1
            )
        # TODO: убрать print
        print(imps)

        # TODO: подумать над тем, а как возвращать каждую из размерностей
        return imps
    def gen_funcs_list(self, fields_files: dict[Field, pathlib.Path]) -> list:
        """
        Метод gen_funcs_list предназначен для динамического определения функции,
        необходимой для обработки определенной строки
        
        :param self: объект типа Collector
        :param fields: словарь типа Field(ключ), pathlib.Path(значение)

        :return: список функций, каждой из которых будет обрабатываться строка
        :rtype: list
        """
        funcs = list()
        
        # for field in fields:
        #     if field.dimension > 1:
        #         funcs.append(
        #             lambda line, line_num,d = field.dimension: self.from_binary_to_hex(line, line_num, d)
        #         )
        #     else:
        #         funcs.append(
        #             self.from_bin_to_bin
        #         )
        
        for field, file in fields_files.items():
            # TODO: поменять захардкоженное значение 1024
            state = self.define_number_system(file, 1024)
            
            if state == NumberSystem.BIN:
                # TODO: убрать print_info()
                message = f"\"{file.name}\" is BINARY"
                print_info(message)

                if field.dimension == 1:
                    funcs.append(
                        self.from_bin_to_bin
                    )
                else:
                    funcs.append(
                        lambda line, line_num, file_name, d = field.dimension: self.from_binary_to_hex(line, line_num, file_name, d)
                    )
            
            if state == NumberSystem.DEC:
                message = f"\"{file.name}\" is DECIMAL"
                print_info(message)
                imp = self.__get_implementation(field.implementation)
                funcs.append(
                    lambda line, line_num, file_name, member_width = imp[-1], depth = imp[-2]: self.from_dec_to_hex(line, line_num, file_name, member_width, depth) 
                )
        return funcs
        
    def collect(self, fields_files: dict[Field, pathlib.Path]) -> pathlib.Path:
        """
        Метод gen_funcs_list предназначена для получения единообразного файла с тестовыми векторами.
        
        :param self: объект типа Collector
        :param fields_files: словарь, в котором каждому объекту типа Field сопоставляется путь до рассматриваемого файла

        :return: путь до сохраненного файла
        :rtype: pathlib.Path
        """
        store_file = self.store_directory / f"vectors_{self.__num_of_calls}.{self.__extension}"

        with open(store_file, "w", buffering=1024*1024) as output_file:
            with ExitStack() as stack:
                wrappers_with_filenames = [
                    (stack.enter_context(open(file, "r", buffering=1024*1024)), file) for file in fields_files.values()
                ]

                files = [wrapper_with_filename[0] for wrapper_with_filename in wrappers_with_filenames]
                files_names = [wrapper_with_filename[1] for wrapper_with_filename in wrappers_with_filenames]

                try:
                    funcs = self.gen_funcs_list(fields_files)
                    line_idx = 0
                    for lines in zip(*files, strict=True):
                        output_file.write(
                            " ".join(f(line, line_idx + 1, file_name) for line, f, file_name in zip(lines, funcs, files_names, strict=True)) + '\n'
                        )
                        line_idx += 1
                except ValueError as e:
                    #  предполагается здесь увидеть исключение вызванное strict=True при создании итерируемого объекта
                    #  может появиться ValueError по другой причине, поэтому надо это иметь ввиду
                    message = str(e)
                    raise CollectorException(message)
        
        self.__num_of_calls += 1
        return store_file