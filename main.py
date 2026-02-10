import csv
import pathlib
import argparse

from output import print_error, print_verbose, print_warning, print_info
from exceptions import ParserException
from classes import Field, FieldValidator, BufferStream, ModuleInfo, InOutFields

class App:
    # статическое поле с описанием полей .csv файла
    __table_fields = [
        "__Implementation__",
        "__Dimension__",
        "__TV_Offset__",
        "__Bit_Position__",
        "__RTL_Signal__",
        "__Model_Signal__",
        "__Doc_Signal__"
    ]

    # статическое поле с индексом рассматриваемой строки 
    __curr_row_index = 0

    def __init__(self, path_config: str, dir: str, verbosity: bool):
        # проверка переданных путей
        self.path_config = pathlib.Path(path_config)
        if not (self.path_config.exists()):
            message = f"File \"{self.path_config.absolute()}\" doesn't exist"
            raise ParserException(message)

        if not (self.path_config.is_file()):
            message = f"\"{self.path_config.absolute()}\" isn't file"
            raise ParserException(message)

        self.dir = pathlib.Path(dir)
        if not (self.dir.exists()):
            message = f"Directory \"{self.dir.absolute()}\" doesn't exist"
            raise ParserException(message)

        if not (self.dir.is_dir()):
            message = f"\"{self.dir.absolute()}\" isn't a directory"
            raise ParserException(message)

        self.verbosity = verbosity
    
    def __read_header(self, buffer_stream: BufferStream) -> ModuleInfo:
        """
        Метод __read_header предназначен для парсинга заголовка .csv конф. файла
        
        :param self: объект класса App
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
                message += f"\"{row[0]}\" doesn't contain \"module\" substring"
                raise ParserException(message)
            
            if "module" in row[2].lower() and "id" in row[2].lower():
                module_id = row[3]
            else:
                message = f"Warning at {self.__curr_row_index} row in a table\n"
                message += f"\"{row[2]}\" doesn't contain \"module\" and \"id\" susbstrings"
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
        
        :param self: объект класса App 
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
                    message = f"\"{delim.join(row)}\" doesn't fit \"^(IN|OUT)PUTS,Total_Bits_(In|Out),\d+,Total_Bytes_(In|Out),\d+,,$\" regex!"
                    raise ParserException(message)
                
                marker = row[0]
                total_bits = row[2]
                total_bytes = row[4]

                row = next(csv_reader)
                self.__curr_row_index += 1

                if row != self.__table_fields:
                    delim = csv_reader.dialect.delimiter
                    message = f"Expected: \"{delim.join(self.__table_fields)}\"\n"
                    message += f"Got: \"{delim.join(row)}\""
                    raise ParserException(message)

                dict_reader = csv.DictReader(buffer_stream, fieldnames=self.__table_fields)
                
                row = next(dict_reader)
                self.__curr_row_index += 1

                while not self.__is_info(list(row.values())):
                    if row["__RTL_Signal__"] or row["__Implementation__"] or row["__Dimension__"]:
                        field = Field(
                                row['__RTL_Signal__'],
                                row['__Implementation__'],
                                row['__Dimension__']
                            )
                        fields.append(field)

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

    def __check_directory(self, fields: list[Field], marker: str, path: pathlib.Path):
        """
        Метод __check_directory предназначен для проверки директорий на наличие файлов с
        похожими именами из fields

        :param self: объект класса App
        :param fields: список полей
        :type fields: list[Field]
        :param marker: строка маркер ("Inputs" или "Outputs")
        :type marker: str
        :param path: путь до директории, в которой необходимо проверять вектор
        :type path: pathlib.Path
        :rtype: str
        """
        field_validator = FieldValidator(fields, marker)
        print(f"=============== {path.absolute()} ===============")
        for child in path.iterdir():
            if not child.is_file():
                continue
            file_name = child.stem
            for field in fields:
                if field.field_name in file_name:
                    field_validator.fields_files[field.field_name] = child.name

        return str(field_validator)
    
    def get_curr_row_index(self):
        """
        Геттeр get_curr_row_index для получения значения закрытого поля __curr_row_index

        :param self: объект класса App
        :rtype: int
        """
        return self.__curr_row_index

    def run(self):
        """
        Основной метод, который запускает парсер.
        Состоит из нескольких этапов:
            1. Считывание заголовка (ModuleInfo)
            2. Перебор функции-генератор и получение объектов типа InOutFields
            3. Вывод дополнительной информации
        :param self: объект класса App
        """
        if self.verbosity:
            message = f"Working with .csv file at \"{self.path_config.absolute()}\"\n"
            message += f"Checking presence of corresponding fields files at \"{self.dir.absolute()}\""
            print_verbose(message)

        with open(self.path_config) as file:
            # получение информации о модуле
            buffer_stream = BufferStream(file)
            module_info = self.__read_header(buffer_stream)
            
            # TODO: подумать о выводе информации только в случае self.__verbosity
            print_info(str(module_info))

            for in_out_fields in self.__get_in_out_fields(buffer_stream):
                message = f"#Type - \"{in_out_fields.marker}\"\n"
                message += f"#Number of bits - {in_out_fields.total_bits}\n"
                message += f"#Number of bytes - {in_out_fields.total_bytes}\n"
                for field in in_out_fields.fields:
                    message += f"#Field - ({None if field.field_name == "" else field.field_name}, {None if field.implementation == "" else field.implementation}, {None if field.dimension == "" else field.dimension})\n"
                message = message.strip()
                print_info(message)

        if self.verbosity:
            print_verbose(f"Total rows read - {self.__curr_row_index}")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='.csv files format parser')
    parser.add_argument('--config', '-c', type=str, default="OTU4_CONVERTER.csv", help='Path to .csv configuration file')
    parser.add_argument('--dir', '-d', default='.', type=str, help='Path to directory where vectors are stored')
    parser.add_argument('--verbose', '-v', action='store_true', help='Switch to verbose mode')
    args = parser.parse_args()
    
    try:
        app = App(args.config, args.dir, args.verbose)
        app.run()
    except ParserException as e:
        print_error(str(e))