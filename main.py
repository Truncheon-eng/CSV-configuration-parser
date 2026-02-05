import csv
from exceptions import ParserException
from classes import Field, FieldValidator
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

    # всего есть одна строка разделитель, представленная в виде ячеек со знаком "-"
    # в OTU4_CONVERTER.csv она просто представлена, как "-,-,-,-,-,-,-"
    # в самом конце, также есть строка полностью состоящая из ",,,,,,"
    # эту строку, а точнее пустые строки рассматривал в качестве разделителя
    @staticmethod
    def __is_delimiter(row: dict):
        result = True
        for cell in row.values():
            if cell != '-'  and cell != '':
                result = False
                break
        return result

    @staticmethod
    def __get_fields(fields: list, marker: str):
        result = list()
        for field in fields:
            result.append(f"[{marker}]: {field}")
        return '\n'.join(result)
    
    # ------------------------ private methods ------------------------
    def __dump_fields(self, csv_reader):
        fields = []
        row = next(csv_reader)
        self.__curr_row_index += 1

        while not (self.__is_delimiter(row)):
            field = Field( # only ParserError
                row['__RTL_Signal__'],
                row['__Implementation__'],
                row['__Dimension__']
            )

            row = next(csv_reader)
            self.__curr_row_index += 1
            fields.append(field)

        return fields

    # ------------------------ private methods ------------------------
    
    def __dump_input_output(self):
        input_fields, output_fields = [], []
        try:
            with open(self.path_config) as config_file:
                for _ in range(2):
                    next(config_file)
                    self.__curr_row_index += 1
                
                csv_reader = csv.DictReader(config_file) # получаем возможность обращения по названиям столбцов
                if csv_reader.fieldnames != self.__table_fields:
                    message = f"Error at {self.__curr_row_index} row in table\n"
                    message += f"Expected: {self.__table_fields}\n"
                    message += f"Got: {csv_reader.fieldnames}"
                    raise ParserException(message)
                self.__curr_row_index += 1

                input_fields = self.__dump_fields(csv_reader)
                if self.verbosity:
                    print(self.__get_fields(input_fields, "Input"))
                    print()

                for _ in range(2):
                    next(csv_reader)
                    self.__curr_row_index += 1
                
                output_fields = self.__dump_fields(csv_reader)
                if self.verbosity:
                    print(self.__get_fields(output_fields, "Output"))
                    print()
        except StopIteration:
            message = f"Error at {self.__curr_row_index} row in table\n"
            message += f"End of file"
            raise ParserException(message)
        
        return input_fields, output_fields

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
        
        input_fields, output_fields = self.__dump_input_output()
        
        print(self.__check_directory(input_fields, "Input", self.dir))
        print()

        out_directory = self.dir / "out_"
        if not (out_directory.exists()):
            message = f"\"{out_directory}\" doesn't exist"
            raise ParserException(message)

        if not (out_directory.is_dir()):
            message = f"\"{out_directory}\" isn't a directory"
            raise ParserException(message)
        
        print(self.__check_directory(output_fields, "Output", out_directory))

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