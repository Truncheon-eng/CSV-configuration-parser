import pathlib
from dataclasses import dataclass
from exceptions import CollectorException
from contextlib import ExitStack
from classes import Field


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
    def from_binary_to_hex(line: str, line_num: int, bit_len: int) -> str:
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
            message = (f"Error at {line_num} string in \"{Collector.from_binary_to_hex.__name__}\"."
                       f" Length of this string is not equal to {bit_len}\n"
                       f"String - \"{line.strip():.30s}\"")

            raise CollectorException(message)
        
        if (bit_len % BIN_TO_HEX_LEN != 0):
            message = (f"Error at {line_num} string in \"{Collector.from_binary_to_hex.__name__}\"."
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
    def from_bin_to_bin(line: str, line_num: int) -> str:
        """
        Метод from_bin_to_bin 0 или 1 из строки с 0 или 1 
        
        :param line: строка, полученная из файла
        :param line_num: номер рассматриваемой строки

        :return: строка с 0 или 1
        :rtype: str
        """
        line = line.strip()
        
        if (len(line) != 1):
            message = (f"Error at {line_num} string in \"{Collector.from_bin_to_bin.__name__}\"."
                        f" Expected only 1 symbol at string\n"
                        f"String - \"{line:.30s}\"")
            raise CollectorException(message)
        
        return line
    
    def gen_funcs_list(self, fields: list[Field]) -> list:
        """
        Метод gen_funcs_list предназначен для динамического определения функции,
        необходимой для обработки определенной строки
        
        :param self: объект типа Collector
        :param fields: список рассматриваемых полей

        :return: список функций, каждой из которых будет обрабатываться строка
        :rtype: list
        """
        funcs = list()
        
        for field in fields:
            if field.dimension > 1:
                funcs.append(
                    lambda line, line_num,d = field.dimension: self.from_binary_to_hex(line, line_num, d)
                )
            else:
                funcs.append(
                    self.from_bin_to_bin
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
                files = [
                    stack.enter_context(
                        open(file, "r", buffering=1024*1024)
                    ) for file in fields_files.values()
                ]
                try:
                    funcs = self.gen_funcs_list(fields_files.keys())
                    line_idx = 0
                    for lines in zip(*files, strict=True):
                        output_file.write(
                            " ".join(f(line, line_idx + 1) for line, f in zip(lines, funcs, strict=True)) + '\n'
                        )
                        line_idx += 1
                except ValueError as e:
                    #  предполагается здесь увидеть исключение вызванное strict=True при создании итерируемого объекта
                    #  может появиться ValueError по другой причине, поэтому надо это иметь ввиду
                    message = str(e)
                    raise CollectorException(message)
        self.__num_of_calls += 1
        return store_file