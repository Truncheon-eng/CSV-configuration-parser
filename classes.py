#!/usr/bin/env python3
class Vector:
    # TODO: по запросу расширить кол-во необходимых полей
    def __init__(self, field_name, implementation, dimension):
        self.field_name = field_name
        self.implementation = implementation
        self.dimension = int(dimension)

    def __str__(self):
        result = (f"Field name: {self.field_name}, "
                  f"Implementation: {'None' if self.implementation == '' else self.implementation}, "
                  f"Dimension: {self.dimension}")
        return result

class FieldValidator:
    def __init__(self, total_fields, marker):
        self.fields_with_files = 0
        self.total_fields = total_fields
        self.fields_files = dict()
        self.blank_fields = list()
        self.marker = marker
    def __str__(self):
        result = list()

        for key, value in self.fields_files.items():
            result.append(f"{self.marker} {key}: file \"{value}\"")
        if len(self.blank_fields) != 0:
            result.append(f"{self.marker} Fields without files: {', '.join(self.blank_fields)}")

        result.append(f"{self.marker} Total fields: {self.total_fields}, "
                      f"Fields with file: {self.fields_with_files}")


        # result.insert(0, "\n")
        result.append("\n")

        return "\n".join(result)