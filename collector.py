import pathlib
from dataclasses import dataclass
from exceptions import CollectorException
from contextlib import ExitStack
from classes import Field

@dataclass(init = False)
class Collector:
    
    __extension = "tv"
    __num_of_calls = 0

    def __init__(self, store_directory: str):
        self.store_directory = pathlib.Path(store_directory)

        if not (self.store_directory.exists()):
            message = f"Directory \"{self.store_directory.absolute()}\" for storing *.(dat|tv) file doesn't exist"
            raise CollectorException(message)

        if not (self.store_directory.is_dir()):
            message = f"\"{self.store_directory.absolute()}\" for storing *.(dat|tv) file isn't a directory"
            raise CollectorException(message)
    
    @staticmethod
    def from_binary_to_hex(line: str, bit_len: int) -> str:
        BIN_TO_HEX_LEN = 8
        HEX_WIDTH = 4

        line_arr = line.strip().split()
        
        # TODO: заменить assert на понятные exceptions
        assert((BIN_TO_HEX_LEN % HEX_WIDTH == 0))
        assert(len(line_arr) == bit_len)
        assert((bit_len % BIN_TO_HEX_LEN) == 0)

        result = list()
        
        for i in range(0, bit_len, BIN_TO_HEX_LEN):
            bin_ = int("".join(line_arr[i:i+BIN_TO_HEX_LEN]), 2)
            result.append(
                hex(bin_)[2:].rjust(BIN_TO_HEX_LEN // HEX_WIDTH, "0")
            )
        
        return ''.join(result)

    @staticmethod
    def from_bin_to_bin(line: str) -> str:
        line = line.strip()
        #TODO: поменять на exceptions
        assert(len(line) == 1)
        return line
    
    def gen_funcs_list(self, fields) -> list:
        funcs = list()
        
        for field in fields:
            if field.dimension > 1:
                funcs.append(
                    lambda line, d = field.dimension: self.from_binary_to_hex(line, d)
                )
            else:
                funcs.append(
                    self.from_bin_to_bin
                )
        
        return funcs
        
    def collect(self, fields_files: dict[Field, pathlib.Path]) -> None:
        
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

                    for lines in zip(*files, strict=True):
                        output_file.write(
                            " ".join(f(line) for line, f in zip(lines, funcs)) + '\n'
                        )

                except ValueError:
                    print("Different number of lines!")
        self.__num_of_calls += 1
        return

        return 