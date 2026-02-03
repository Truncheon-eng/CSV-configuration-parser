import csv
from exceptions import ParserException
from classes import Vector, FieldValidator
import pathlib
import argparse

curr_row_index = 0

table_fields = [
    "__Implementation__",
    "__Dimension__",
    "__TV_Offset__",
    "__Bit_Position__",
    "__RTL_Signal__",
    "__Model_Signal__",
    "__Doc_Signal__"
]


def is_delimiter(row):
    value = True
    for elem in row.values():
        if elem != '-' and elem != '':
            value = False
            break
    return value


def get_vectors(reader):
    global curr_row_index
    list_vectors = list()
    row = next(reader)
    curr_row_index += 1
    while not (is_delimiter(row)):
        vector = Vector(
            row['__RTL_Signal__'],
            row['__Implementation__'],
            row['__Dimension__']
        )
        row = next(reader)
        curr_row_index += 1
        list_vectors.append(vector)

    return list_vectors

def check_directory(vectors, marker, path):
    field_validator = FieldValidator(
        len(vectors),
        marker
    )
    # проверяем текущую директорию
    for child in path.iterdir():
        if not child.is_file():
            continue

        file_name = child.stem
        for vec in vectors:
            # field_validator.fields_files[vec.field_name] = None
            if vec.field_name in file_name:
                field_validator.fields_with_files += 1
                field_validator.fields_files[vec.field_name] = child.name
    
    for vec in vectors:
        if not vec.field_name in field_validator.fields_files:
            field_validator.blank_fields.append(vec.field_name)

    print(str(field_validator))
    return

def dump_vectors(file_name):
    global curr_row_index
    input_vectors, output_vectors = list(), list()
    with open(file_name) as csv_file:
        # пока исхожу из предположения, что Input поля идут первыми, а Output поля вторыми
        for _ in range(2):  # информация о модуле
            next(csv_file)
            curr_row_index += 1

        reader = csv.DictReader(csv_file)
        if not (reader.fieldnames == table_fields):
            message = f"{reader.fieldnames} != {table_fields}"
            raise ParserException(curr_row_index, message, file_name)
        curr_row_index += 1

        input_vectors = get_vectors(reader)

        for _ in range(2):
            next(reader)
            curr_row_index += 1

        output_vectors = get_vectors(reader)

    return input_vectors, output_vectors

def print_vectors_information(vectors, marker):
    result = list()
    for vec in vectors:
        result.append(f"{marker} {str(vec)}")

    # result.insert(0, "\n")
    result.append("\n")
    print('\n'.join(result))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='.csv files format parser')
    parser.add_argument('--config', '-c', type=str, default="OTU4_CONVERTER.csv", help='Path to .csv configuration file')
    parser.add_argument('--dir', '-d', default='.', type=str, help='Path to directory where vectors stored')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print debug information')
    args = parser.parse_args()

    path_config = pathlib.Path(args.config)
    directory = pathlib.Path(args.dir)
    verbosity = args.verbose

    if (not path_config.exists()) or (not path_config.is_file()):
        raise Exception(f"No such file {str(path_config)}")
    
    if (not directory.exists()) or (not directory.is_dir()):
        raise Exception(f"No such directory {str(directory)}")
    
    input_vectors, output_vectors = dump_vectors(path_config)

    if args.verbose:
        print(f"[Verbose] Read strings: {curr_row_index}")
        print_vectors_information(input_vectors, '[Input]')
        print_vectors_information(input_vectors, '[Output]')
    if args.verbose:
        print(f"Working with input vectors in {directory.absolute()}")
    check_directory(input_vectors, '[Input]', directory)
    
    out_directory = pathlib.Path(directory) / "out_"
    if out_directory.exists() and out_directory.is_dir():
        if args.verbose:
            print(f"Working with output vectors in {out_directory.absolute()}")
        check_directory(output_vectors, '[Output]', out_directory)
    else:
        print(f"There is not out_ directory in {str(out_directory)}")