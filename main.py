import csv
from exceptions import ParserException
from classes import Field, FieldValidator, BufferStream, ModuleInfo, InOutFields
import pathlib
import argparse


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

    # статическое поле verbosity
    __verbosity_marker = '[i]'
    def __init__(self, path_config: str, dir: str, verbosity: bool):
        # проверка переданных путей
        self.path_config = pathlib.Path(path_config)
        if not (self.path_config.exists()):
            message = f"\"{self.path_config}\" doesn't exist"
            raise ParserException(message)

        if not (self.path_config.is_file()):
            message = f"\"{self.path_config}\" isn't file"
            raise ParserException(message)

        self.dir = pathlib.Path(dir)
        if not (self.dir.exists()):
            message = f"\"{self.dir}\" doesn't exist"
            raise ParserException(message)

        if not (self.dir.is_dir()):
            message = f"\"{self.dir}\" isn't a directory"
        
        self.verbosity = verbosity

    """
    Функция парсер заголовка метаданных модуля
        buffer_stream - поток ввода с буферизацией
    """
    def __read_header(self, buffer_stream: BufferStream) -> ModuleInfo:
        module_info = None
        try:
            csv_reader = csv.reader(buffer_stream)
            
            row = next(csv_reader)
            self.__curr_row_index += 1

            if len(row) != 7:
                message = f"Error at {self.__curr_row_index} row\n"
                message += f"\"{f"{csv_reader.dialect.delimiter}".join(row)}\" doesn't contain 7 cells"
                raise ParserException(message)

            module, module_id = str(), str()

            if "module" in row[0].lower():
                module = row[1]
            else:
                message = f"Error at {self.__curr_row_index} row in a table\n"
                message += f"\"{row[0]}\" doesn't contain \"module\" substring!"
                raise ParserException(message)
            
            if "module" in row[2].lower() and "id" in row[2].lower():
                module_id = row[3]
            else:
                message = f"{self.__verbosity_marker} Warning at {self.__curr_row_index} row in a table\n"
                message += f"{self.__verbosity_marker} \"{row[2]}\" doesn't contain \"module\" and \"id\" susbstrings1"
                print(message)
            
            module_info = ModuleInfo(
                module, module_id
            )

        except StopIteration:
            message = f"Stopped at {self.__curr_row_index} row when executed __read_header\n"
            message += f"End of file"
            raise ParserException(message)

        return module_info

    """
    Функция генератор, возвращаю объекты тип InOutFields
        buffer_stream - объект типа BufferStream (поток ввода)
    """
    def __get_in_out_fields(self, buffer_stream: BufferStream):
        try:
            while not buffer_stream.eof():
                fields = list()
                csv_reader = csv.reader(buffer_stream)
                
                row = next(csv_reader)
                # TODO: каким-то образом необходимо проверять, что кол-во ячеек равно 7
                assert(len(row) == 7)
                self.__curr_row_index += 1

                if not self.__is_info(row):
                    message = f"\"{f"{csv_reader.dialect.delimiter}".join(row)}\" doesn't represent the information!"
                    raise ParserException(message)
                
                marker = row[0]
                total_bits = row[2]
                total_bytes = row[4]

                row = next(csv_reader)
                # TODO: каким-то образом необходимо проверять, что кол-во ячеек равно 7
                assert(len(row) == 7)
                self.__curr_row_index += 1

                if row != self.__table_fields:
                    message = f"Expected: \"{f"{csv_reader.dialect.delimiter}".join(self.__table_fields)}\"\n"
                    message += f"Got: \"{f"{csv_reader.dialect.delimiter}".join(row)}\""
                    raise ParserException(message)

                dict_reader = csv.DictReader(buffer_stream, fieldnames=self.__table_fields)
                
                row = next(dict_reader)
                # TODO: каким-то образом необходимо проверять, что кол-во ячеек равно 7
                assert(len(row) == 7)
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
                    # TODO: каким-то образом необходимо проверять, что кол-во ячеек равно 7
                    assert(len(row) == 7)
                    self.__curr_row_index += 1
                
                if not buffer_stream.eof():
                    buffer_stream.step_back()
                
                yield InOutFields(
                    marker,
                    total_bits,
                    total_bytes,
                    fields
                )
        except StopIteration:
            message = f"Stopped at {self.__curr_row_index} row when executed __get_in_out_fields\n"
            message += f"End of file"
            raise ParserException(message)
    
    """
    Паттерн:
        [INPUTS/OUTPUTS],Total_Bits_...,[int],Total_Bytes_...,[int],,
    Возвращает true если строка является "информационной", false - в противном случае
        row: list[str] - массив ячекк переданной строки
    """
    @staticmethod
    def __is_info(row: list[str]) -> bool:
        if not "inputs" in row[0].lower() and not "outputs" in row[0].lower():
            return False
        
        if not "bits" in row[1].lower():
            return False
        
        if not "bytes" in row[3].lower():
            return False
    
        return True


    @staticmethod
    def __get_fields(fields: list, marker: str):
        result = list()
        for field in fields:
            result.append(f"[{marker}]: {field}")
        return '\n'.join(result)


    def __check_directory(self, fields: list, marker: str, path: pathlib.Path):
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
        return self.__curr_row_index

    def run(self):
        if self.verbosity:
            print(f"{self.__verbosity_marker}: Working with .csv file at \"{self.path_config.absolute()}\"")
            print(f"{self.__verbosity_marker}: Checking presence of corresponding fields files at \"{self.dir.absolute()}\"")
            print()
        
        with open(self.path_config) as file:
            # получение информации о модуле
            buffer_stream = BufferStream(file)
            module_info = self.__read_header(buffer_stream)
            
            print(module_info)

            for in_out_fields in self.__get_in_out_fields(buffer_stream):
                print(f"{self.__verbosity_marker} {in_out_fields.marker}")
                print(f"{self.__verbosity_marker} #bits {in_out_fields.total_bits}")
                print(f"{self.__verbosity_marker} #bytes {in_out_fields.total_bytes}")
                for field in in_out_fields.fields:
                    print(f"\t{self.__verbosity_marker} {field.field_name} {field.implementation} {field.dimension}")

        if self.verbosity:
            print(f"{self.__verbosity_marker}: Total rows read - {self.__curr_row_index}")
        
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='.csv files format parser')
    parser.add_argument('--config', '-c', type=str, default="OTU4_CONVERTER.csv", help='Path to .csv configuration file')
    parser.add_argument('--dir', '-d', default='.', type=str, help='Path to directory where vectors stored')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print debug information')
    args = parser.parse_args()
    
    try:
        app = App(args.config, args.dir, args.verbose)
        app.run()
    except ParserException as e:
        print(e)
    # except Exception as e:
    #     print(f"Undefined error: {e}")