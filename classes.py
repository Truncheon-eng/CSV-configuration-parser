from exceptions import ParserException

class Field:
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

    # def __eq__(self, other):
    #     return  self.field_name == other.field_name and self.implementation == other.implementation and self.dimension == self.dimension
    
    # def __hash__(self):
    #     # TODO: подумать насколько вообщехорошо делать такого рода хеш в объектк с тремя полями
    #     return hash(self.field_name)

class FieldValidator:
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
                result.append(f"{self.marker}: {key} - file \"{value}\"")
                with_files += 1
            else:
                without_files.append(str(key))
            total += 1

        result.append(f"{self.marker}: Number of fields with files - {with_files}; Total number of fields - {total}")
        if len(without_files) != 0:
            result.append(f"{self.marker}: Fields without files - {', '.join(without_files)}")
        return "\n".join(result)


class InOutFields:
    """
    Данный клас содержит в себе всю необходимую информацию:
        marker - входные / выходные вектора
        total_bits - общее кол-во битов входных / выходных векторов
        total_bytes - общее кол-во байтов входных / выходных векторов
        fields - массивы полей входных / выходных векторов
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
            message = f"\"{total_bits}\" in Total_Bits_... can't be interpreted as integer value!"
            raise ParserException(message)
        
        try:
            self.total_bytes = int(total_bytes)
        except (ValueError, TypeError):
            message = f"\"{total_bytes}\" in Total_Bytes_... can't be interpreted as integer value!"
            raise ParserException(message)

        self.fields = fields
        
class ModuleInfo:
    """
    Класс для хранения информации модуля
    Пока добавлены два поля: 
        module: название самого модуля(то что следует за __Module__ в .csv файле)
        module_id: в большинстве .csv файлов отсутствовал
    """
    def __init__(self, module: str, module_id: str):
        # TODO: насколько помню не везде присутствует __Subsystems__
        # TODO: насколько целесообразно тогда добавлять эти поля
        self.module = module
        try:
            self.module_id = int(module_id)
        except (TypeError, ValueError):
            print(f"[i] \"{module_id}\" value can't be interpreted as integer")
            self.module_id = None
    
    
    def __str__(self):
        result = f"[i] Module: {self.module}\n"
        result += f"[i] Module ID: {self.module_id}"
        return result


class BufferStream:
    """
    Класс для буферизированного вывода строк.
    Размер буфера равен одной строке.
    Вызов метода step_back приводит к исключению.
    """
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
        
        return self.last_line

    """
    step_back - указывает на то, что последнюю 
    полученную строку нужно переиспользовать
    Args:
        self
    Returns:
        None
    """
    def step_back(self) -> None:
        if self.is_waiting:
            message = "double call of step_back in BufferStream isntance"
            raise ParserException(message)
        self.is_waiting = True
        return
    
    """
    eof - определяет закончился ли файл или нет
    Args:
        self
    Returns:
        bool - (True - конец файла / False - еще не закончился)
    """
    def eof(self) -> bool:
        symbol = self.file.read(1)
        
        if symbol:
            self.file.seek(self.file.tell() - 1)
            return False
        
        if self.is_waiting:
            return False

        return True