import csv
import pathlib
import argparse
import re

from output import print_error, print_verbose, print_warning, print_info
from exceptions import ParserException, CollectorException
from classes import Field, FieldValidator, BufferStream, ModuleInfo, InOutFields
from collector import Collector

from datetime import datetime


class Parser:
    #TODO: поменять документацию в соотв. с новыми добавленными полями
    """
    Класс приложения-парсера, необходимый для запуска самого парсера.
    
    :ivar __table_fields: Список названий полей соотв. ячеек.
    :vartype __table_fields: list[str]
    
    :ivar __curr_row_index: Индекс текущей рассматривавемой строки.
    :vartype __curr_row_index: int

    :ivar path_config: Путь до .csv конфигурационного файла.
    :vartype path_config: pathlib.Path

    :ivar input: Путь до директории, в которой предположительно находятся входные тестовые вектора.
    :vartype input: pathlib.Path

    :ivar output: Путь до директории, в которой предположительно находятся выходные тестовые вектора.
    :vartype output: pathlib.Path

    :ivar verbosity: Параметр "многословности", определяющий необходимо ли выводить дополнительную информацию.
    :vartype verbosity: bool
    """
    __table_fields = [
        "__Implementation__",
        "__Dimension__",
        "__TV_Offset__",
        "__Bit_Position__",
        "__Type__",
        "__RTL_Signal__",
        "__Model_Signal__",
        "__Doc_Signal__"
    ]

    # статическое поле с индексом рассматриваемой строки 
    __curr_row_index = 0

    def __init__(self, path_config: str, input: str, output: str, verbosity: bool):
        # проверка переданных путей
        self.path_config = pathlib.Path(path_config)
        if not (self.path_config.exists()):
            message = f"File \"{self.path_config.absolute()}\" doesn't exist"
            raise ParserException(message)

        if not (self.path_config.is_file()):
            message = f"\"{self.path_config.absolute()}\" isn't file"
            raise ParserException(message)

        self.input = pathlib.Path(input)
        if not (self.input.exists()):
            message = f"Directory \"{self.input.absolute()}\" for input vectors doesn't exist"
            raise ParserException(message)

        if not (self.input.is_dir()):
            message = f"\"{self.input.absolute()}\" for input vectors isn't a directory"
            raise ParserException(message)

        self.output = pathlib.Path(output)
        if not (self.output.exists()):
            message = f"Directory \"{self.output.absolute()}\" for output vectors doesn't exist"
            raise ParserException(message)

        if not (self.output.is_dir()):
            message = f"\"{self.output.absolute()}\" for output vectors isn't a directory"
            raise ParserException(message)
        
        self.verbosity = verbosity
    
    def __read_header(self, buffer_stream: BufferStream) -> ModuleInfo:
        """
        Метод __read_header предназначен для парсинга заголовка .csv конф. файла
        
        :param self: объект класса Parser
        :param buffer_stream: поток ввода с буферизацией
        :type buffer_stream: BufferStream
        :return: объект ModuleInfo, содержащий информацию о заголовке .csv файла
        :rtype: ModuleInfo
        """
        module_info = None
        try:
            csv_reader = csv.reader(buffer_stream)
            
            row = next(csv_reader)
            self.__curr_row_index += 1

            module, module_id = str(), str()

            if "module" in row[0].lower():
                module = row[1]
            else:
                message = f"Error at {self.__curr_row_index} row in a table\n"
                message += f"\"{row[0]:.30s}\" doesn't contain \"module\" substring"
                raise ParserException(message)
            
            if "module" in row[2].lower() and "id" in row[2].lower():
                module_id = row[3]
            else:
                message = f"Warning at {self.__curr_row_index} row in a table\n"
                message += f"\"{row[2]:.30s}\" doesn't contain \"module\" and \"id\" susbstrings"
                print_warning(message)
            
            module_info = ModuleInfo(
                module, module_id
            )

        except StopIteration:
            message = f"Stopped at {self.__curr_row_index} row, when executed {self._App__read_header.__name__}\n"
            message += f"End of file"
            raise ParserException(message)

        return module_info

    
    def __get_in_out_fields(self, buffer_stream: BufferStream):
        """
        Метод-генератор __get_in_out_fields предназначен для получения объектов типа InOutFields 
        
        :param self: объект класса Parser 
        :param buffer_stream: поток ввода с буферизацией
        :type buffer_stream: BufferStream
        """
        try:
            while not buffer_stream.eof():
                fields = list()
                csv_reader = csv.reader(buffer_stream)
                
                row = next(csv_reader)
                self.__curr_row_index += 1

                if not self.__is_info(row):
                    delim = csv_reader.dialect.delimiter
                    message = f"\"{delim.join(row):.30s}\" doesn't fit \"^(IN|OUT)PUTS,Total_Bits_(In|Out),\\d+,Total_Bytes_(In|Out),\\d+,,$\" regex!"
                    raise ParserException(message)
                
                marker = row[0]
                total_bits = row[2]
                total_bytes = row[4]

                row = next(csv_reader)
                self.__curr_row_index += 1

                if row != self.__table_fields:
                    delim = csv_reader.dialect.delimiter
                    message = f"Expected: \"{delim.join(self.__table_fields):.30s}\"\n"
                    message += f"Got: \"{delim.join(row):.30s}\""
                    raise ParserException(message)

                dict_reader = csv.DictReader(buffer_stream, fieldnames=self.__table_fields)
                
                row = next(dict_reader)
                self.__curr_row_index += 1

                while not self.__is_info(list(row.values())):
                    if  row["__RTL_Signal__"] or \
                        row["__Implementation__"] or \
                        row["__Dimension__"] or \
                        row["__Model_Signal__"]:
                        
                        simulating = True

                        if row['__Type__'] == 'S':
                            simulating = True
                        elif row['__Type__'] == 'R':
                            simulating = False
                        else:
                            message = f"#Field - {row['__RTL_Signal__']}; __Type__ should be S or R"
                            raise ParserException(message)

                        dimension = 0

                        try:
                            dimension = int(row['__Dimension__'])
                        except (ValueError, TypeError):
                            message = f"#Field - {row['__RTL_Signal__']}; __Dimension__ \"{row['__Dimension__']}\" must be an integer"
                            raise ParserException(message)
                        
                        field = Field(
                            row['__RTL_Signal__'],
                            row['__Model_Signal__'],
                            row['__Implementation__'],
                            simulating,
                            dimension
                        )

                        if field.simulating:
                            fields.append(field)
                        else:
                            message = (
                                f"#Field - {str(field)}\n"
                                f"\"{field.rtl_signal}\" seems to be non-simulating, therefore skip this field"        
                            )
                            print_info(message)



                    if (buffer_stream.eof()):
                        break

                    row = next(dict_reader)
                    self.__curr_row_index += 1
                
                if not buffer_stream.eof():
                    buffer_stream.step_back()
                    self.__curr_row_index -= 1
                
                yield InOutFields(
                    marker,
                    total_bits,
                    total_bytes,
                    fields
                )
        except StopIteration:
            message = f"Stopped at {self.__curr_row_index} row, when executed {self._App__get_in_out_fields.__name__}\n"
            message += f"End of file"
            raise ParserException(message)
    
    @staticmethod
    def __is_info(row: list[str]) -> bool:
        """
        Статиеский метод __is_info предназначен для определения того факта, 
        явялется ли очередная считанная строка "информационной"
        
        :param row: список ячеек, считанной строки
        :type row: list[str]
        :return: bool-во значение, определяющее является ли строка "информационной"
        :rtype: bool
        """
        if not "inputs" in row[0].lower() and not "outputs" in row[0].lower():
            return False
        
        if not "bits" in row[1].lower():
            return False
        
        if not "bytes" in row[3].lower():
            return False
    
        return True

    def __check_directory(self, fields: list[Field], marker: str, path: pathlib.Path) -> FieldValidator:
        """
        Метод __check_directory предназначен для проверки директорий на наличие файлов с
        похожими именами из fields

        :param self: объект класса Parser
        :param fields: список полей
        :type fields: list[Field]
        :param marker: строка маркер ("INPUTS" или "OUTPUTS")
        :type marker: str
        :param path: путь до директории, в которой необходимо проверять вектор
        :type path: pathlib.Path
        :rtype: str
        """
        field_validator = FieldValidator(fields, marker)

        print(f"=============== {path.absolute()} ===============")

        for field in fields:
            
            pattern_string = rf"{"in" if marker.lower() == 'inputs' else 'out'}_{field.model_signal}(\[\d+\]|\(\d+u\))\.dat"
            pattern = re.compile(pattern_string) # compiled regex for searching important files

            for child in path.iterdir():
                if not child.is_file():
                    continue
            
                file_name = child.name
                # exp_file_name = f"{"in" if marker.lower() == 'inputs' else 'out'}_{field.model_signal}"

                # if exp_file_name in file_name:
                #     field_validator.associate_with_file(field, child)
                if re.search(pattern, file_name):
                    field_validator.associate_with_file(field, child)
            
            if not field_validator.check_field(field):
                message = f"There is not file in \"{path}\" which is associated with \"{field.rtl_signal}\""
                print_warning(message)

        return field_validator
    
    def get_curr_row_index(self):
        """
        Геттeр get_curr_row_index для получения значения закрытого поля __curr_row_index

        :param self: объект класса Parser
        :rtype: int
        """
        return self.__curr_row_index

    def run(self) -> list[dict[Field, pathlib.Path]]:
        """
        Основной метод, который запускает парсер.
        Состоит из нескольких этапов:
            1. Считывание заголовка (ModuleInfo)
            2. Перебор функции-генератор и получение объектов типа InOutFields
            3. Вывод дополнительной информации
        :param self: объект класса Parser
        """
        if self.verbosity:
            message = f"Working with .csv file at \"{self.path_config.absolute()}\"\n"
            message += f"Checking presence of corresponding fields files at \"{self.input.absolute()}\" for input vectors\n"
            message += f"Checking presence of corresponding fields files at \"{self.output.absolute()}\" for output vectors"
            print_verbose(message)

        in_outs = list()
        result = list()

        with open(self.path_config) as file:
            # получение информации о модуле
            buffer_stream = BufferStream(file)
            module_info = self.__read_header(buffer_stream)
            
            # TODO: подумать о выводе информации только в случае self.__verbosity
            print_info(str(module_info))

            for in_out_fields in self.__get_in_out_fields(buffer_stream):
                # append необходим в дальнейшем для проверки наличия полей в директории
                in_outs.append(in_out_fields)

                # информационная часть
                message = f"#Type - \"{in_out_fields.marker}\"\n"
                message += f"#Number of bits - {in_out_fields.total_bits}\n"
                message += f"#Number of bytes - {in_out_fields.total_bytes}\n"
                
                for field in in_out_fields.fields:
                    message += f"#Field - {str(field)}\n"

                message = message.strip()
                print_info(message)
        
        for in_out_fields in in_outs:
            fv = None 

            #TODO: убрать отсюда print
            if in_out_fields.marker.lower() == "inputs":
                fv = self.__check_directory(
                    in_out_fields.fields,
                    in_out_fields.marker,
                    self.input
                )
            
            if in_out_fields.marker.lower() == "outputs":
                fv = self.__check_directory(
                    in_out_fields.fields,
                    in_out_fields.marker,
                    self.output
                )

            print_info(str(fv))
            result.append(fv.fields_files)

        if self.verbosity:
            print_verbose(f"Total rows read - {self.__curr_row_index}")
        
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='.csv files format parser and handler')
    parser.add_argument('--config', '-c', type=str, default="OTU4_CONVERTER.csv", help='Path to .csv configuration file')
    parser.add_argument('--input-directory', '-i', default='.', type=str, help='Path to directory where input vectors are stored')
    parser.add_argument('--output-directory', '-o', default='.', type=str, help='Path to directory where output vectors are stored')
    parser.add_argument('--verbose', '-v', action='store_true', help='Switch to verbose mode')
    parser. add_argument('--store', '-s', default='.', type=str, help='Path to directory where *.(dat|tv) files')
    args = parser.parse_args()
    
    try:
        start = datetime.now()

        parser = Parser(args.config, args.input_directory, args.output_directory, args.verbose)
        parser_results = parser.run()

        collector = Collector(args.store)
        
        for result in parser_results:
            store_file = collector.collect(result)
            if args.verbose:
                message = f"Vectores are stored at \"{store_file.absolute()}\""
                print_verbose(message)        

        end = datetime.now()
        print(f"Total time - {end - start}")
    
    except (ParserException, CollectorException) as e:
        print_error(str(e))
