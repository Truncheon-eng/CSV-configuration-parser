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