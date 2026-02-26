# CSV-configuration-parser
```shell
python3 main.py -h                                                           
usage: main.py [-h] [--config CONFIG] [--input-directory INPUT_DIRECTORY] [--output-directory OUTPUT_DIRECTORY] [--verbose] [--store STORE] [--dump-size DUMP_SIZE]

.csv files format parser and handler

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to .csv configuration file
  --input-directory INPUT_DIRECTORY, -i INPUT_DIRECTORY
                        Path to directory where input vectors are stored
  --output-directory OUTPUT_DIRECTORY, -o OUTPUT_DIRECTORY
                        Path to directory where output vectors are stored
  --verbose, -v         Switch to verbose mode
  --store STORE, -s STORE
                        Path to directory where *.(dat|tv) files
  --dump-size DUMP_SIZE, -d DUMP_SIZE
                        Number of bits to be read in order to identify number system (1024 <= dump_size <= 8192)
```
`--config` - путь до .csv файла с расписанной конфигурацией определенных структур (например `OTU4_CONVERTER.csv`).

`--input-directory` - путь до директории, в которой сохранены входные вектора (INPUTS).

`--output-directory` - путь до директории, в которой сохранены выходные вектора (OUTPUTS).

`--verbose` - вывод дополнительной информации. Например, полный путь до директорий, в которых хранятся входные/выходные вектора.

`--store` - директория, в которой необходимо сохранить единые тестовые вектора

`--dump-size` - кол-во символов, которое необходимо считать, чтобы определить систему счисления использованную в файле

Пример вызвова:
```shell
python3 main.py \
  \ -c "/home/truncheon/omo_testchamber/DOCs/Test Vectors/FRAMER_PCS_TX/DESCRAMBLER.csv"
  \ -i "/home/truncheon/no_errors/PCSTX/descrambler/" 
  \ -o "/home/truncheon/no_errors/PCSTX/descrambler/" 
  \ -s "./vectors" 
  \ --dump-size=2048
  \ -v

[v]: Working with .csv file at "/home/truncheon/omo_testchamber/DOCs/Test Vectors/FRAMER_PCS_TX/DESCRAMBLER.csv"
[v]: Checking presence of corresponding fields files at "/home/truncheon/no_errors/PCSTX/descrambler" for input vectors
[v]: Checking presence of corresponding fields files at "/home/truncheon/no_errors/PCSTX/descrambler" for output vectors

[!]: Warning at 1 row in a table
[!]: "" doesn't contain "module" and "id" susbstrings

[!]: "" value can't be interpreted as integer, when reading ModuleInfo

[v]: Module: DESCRAMBLER
[v]: Module ID: None

[i]: #Field - {
[i]:    .rtl_signal = "AIS_EN_IN",
[i]:    .model_signal = "AIS_EN_IN",
[i]:    .simulating = "False"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: "AIS_EN_IN" seems to be non-simulating, therefore skip this field

[i]: #Type - "INPUTS"
[i]: #Number of bits - 136
[i]: #Number of bytes - 17
[i]: #Field - {
[i]:    .rtl_signal = "DATA_IN",
[i]:    .model_signal = "DATA_IN",
[i]:    .simulating = "True"
[i]:    .implementation = "[127:0]",
[i]:    .dimension = "128"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "DATA_VALID",
[i]:    .model_signal = "DATA_VALID_IN",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "FRAME_BEGIN",
[i]:    .model_signal = "FRAME_BEGIN_IN",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "nHARD_RESET",
[i]:    .model_signal = "nHARD_RESET",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }

[i]: #Type - "OUTPUTS"
[i]: #Number of bits - 136
[i]: #Number of bytes - 17
[i]: #Field - {
[i]:    .rtl_signal = "DATA_OUT",
[i]:    .model_signal = "DATA_OUT",
[i]:    .simulating = "True"
[i]:    .implementation = "[127 : 0]",
[i]:    .dimension = "128"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "DATA_VALID_OUT",
[i]:    .model_signal = "DATA_VALID_OUT",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }
[i]: #Field - {
[i]:    .rtl_signal = "FRAME_BEGIN_OUT",
[i]:    .model_signal = "FRAME_BEGIN_OUT",
[i]:    .simulating = "True"
[i]:    .implementation = "",
[i]:    .dimension = "1"
[i]: }

=============== /home/truncheon/no_errors/PCSTX/descrambler ===============
[i]: INPUTS; "DATA_IN" - file "in_DATA_IN(1u).dat"
[i]: INPUTS; "DATA_VALID" - file "in_DATA_VALID_IN(1u).dat"
[i]: INPUTS; "FRAME_BEGIN" - file "in_FRAME_BEGIN_IN(1u).dat"
[i]: INPUTS; "nHARD_RESET" - file "in_nHARD_RESET(1u).dat"
[i]: INPUTS; Number of fields with files - 4; Total number of fields - 4

=============== /home/truncheon/no_errors/PCSTX/descrambler ===============
[i]: OUTPUTS; "DATA_OUT" - file "out_DATA_OUT(1u).dat"
[i]: OUTPUTS; "DATA_VALID_OUT" - file "out_DATA_VALID_OUT(1u).dat"
[i]: OUTPUTS; "FRAME_BEGIN_OUT" - file "out_FRAME_BEGIN_OUT(1u).dat"
[i]: OUTPUTS; Number of fields with files - 3; Total number of fields - 3

[v]: Total rows read - 14

[v]: "in_DATA_IN(1u).dat" seems to be BINARY

[v]: "in_DATA_VALID_IN(1u).dat" seems to be BINARY

[v]: "in_FRAME_BEGIN_IN(1u).dat" seems to be BINARY

[v]: "in_nHARD_RESET(1u).dat" seems to be BINARY

[v]: Vectores are stored at "/home/truncheon/CSV-configuration-parser/vectors/vectors_0.tv"

[v]: "out_DATA_OUT(1u).dat" seems to be BINARY

[v]: "out_DATA_VALID_OUT(1u).dat" seems to be BINARY

[v]: "out_FRAME_BEGIN_OUT(1u).dat" seems to be BINARY

[v]: Vectores are stored at "/home/truncheon/CSV-configuration-parser/vectors/vectors_1.tv"

Total time - 0:00:23.908457

```
