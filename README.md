# CSV-configuration-parser
```shell
python3 main.py -h 
usage: main.py [-h] [--config CONFIG] [--dir DIR] [--verbose]

.csv files format parser

options:
  -h, --help           show this help message and exit
  --config, -c CONFIG  Path to .csv configuration file
  --dir, -d DIR        Path to directory where vectors stored
  --verbose, -v        Print debug information
```
`--config` - путь до .csv файла с расписанной конфигурацией определенных структур (например `OTU4_CONVERTER.csv`).

`--dir` - путь до директории самого модуля (например в архиве `no_errors` input и output вектора находились в директории `no_errors/PCSTX/otu4_converter` и `no_errors/PCSTX/otu4_converter/out_` соответсвенно)

`-v` - вывод дополнительной информации. Например, функция `dump_vectors` возвращает два массива с входными и выходными полями соотв., аргумент `--verbose` выводит все поля и атрибуты этих полей (`__RTL_Signal__`, `__Implementation__`, `__Dimension__`).

Для получения полей пользовался таким подходом:
- первая строка файла (OTU4_CONVERTER.csv) - метаинформация модуля
- вторая строка -  информация о том, какое кол-во бит и байт входного у вектора
- третья строка заголовки (считваю их через `DictRead` файла .csv)
- n-ое кол-во строк для входных векторов - сами поля с их метаинформацией
- n + 4 строка - разделитель в виде строки из `-`
- n + 5 строка - те же самые заголовки полей
- m-ое кол-во строк для выходных векторов - сами поля с их метаинформацией
- m + n + 6 строк - пробелы разделители

Пример вызвова:
```shell
python3 main.py -c /home/kali/CSV-configuration-parser/OTU4_CONVERTER.csv
  \-d /mnt/hgfs/kali_shared/vector_unification/no_errors/PCSTX/otu4_converter/ -v
[Verbose] Read strings: 37
[Input] Field name: DATA_IN, Implementation: [9:0][31:0], Dimension: 320
[Input] Field name: DATA_VALID_IN, Implementation: None, Dimension: 1
[Input] Field name: nHARD_RESET, Implementation: None, Dimension: 1
[Input] Field name: DEFAULT_LOGICAL_LANES_SEARCH_ORDER, Implementation: [19:0][4:0], Dimension: 104
[Input] Field name: FAS_MATCH_REQUIRED, Implementation: [5:0], Dimension: 8
[Input] Field name: OTL_10_UNLOCKS_TO_RESET, Implementation: [4:0], Dimension: 8
[Input] Field name: OTU4_CONVERTER_RESET, Implementation: None, Dimension: 1


[Output] Field name: DATA_IN, Implementation: [9:0][31:0], Dimension: 320
[Output] Field name: DATA_VALID_IN, Implementation: None, Dimension: 1
[Output] Field name: nHARD_RESET, Implementation: None, Dimension: 1
[Output] Field name: DEFAULT_LOGICAL_LANES_SEARCH_ORDER, Implementation: [19:0][4:0], Dimension: 104
[Output] Field name: FAS_MATCH_REQUIRED, Implementation: [5:0], Dimension: 8
[Output] Field name: OTL_10_UNLOCKS_TO_RESET, Implementation: [4:0], Dimension: 8
[Output] Field name: OTU4_CONVERTER_RESET, Implementation: None, Dimension: 1


Working with input vectors in /mnt/hgfs/kali_shared/vector_unification/no_errors/PCSTX/otu4_converter
[Input] DATA_IN: file "in_DATA_IN(32u).dat"
[Input] DATA_VALID_IN: file "in_DATA_VALID_IN(1u).dat"
[Input] DEFAULT_LOGICAL_LANES_SEARCH_ORDER: file "in_DEFAULT_LOGICAL_LANES_SEARCH_ORDER(5u).dat"
[Input] FAS_MATCH_REQUIRED: file "in_FAS_MATCH_REQUIRED(6u).dat"
[Input] nHARD_RESET: file "in_nHARD_RESET(1u).dat"
[Input] OTL_10_UNLOCKS_TO_RESET: file "in_OTL_10_UNLOCKS_TO_RESET(5u).dat"
[Input] OTU4_CONVERTER_RESET: file "in_OTU4_CONVERTER_RESET(1u).dat"
[Input] Total fields: 7, Fields with file: 7


Working with output vectors in /mnt/hgfs/kali_shared/vector_unification/no_errors/PCSTX/otu4_converter/out_
[Output] DATA_VALID_OUT: file "DATA_VALID_OUT_D(1u).dat"
[Output] FRAME_BEGIN: file "FRAME_BEGIN(1u).dat"
[Output] INPUT_DATA_VALID_RATE: file "INPUT_DATA_VALID_RATE(17u).dat"
[Output] LAST_FAS_DETECTION_DEGREE: file "LAST_FAS_DETECTION_DEGREE(4u).dat"
[Output] LAST_FAS_DISTANCE: file "LAST_FAS_DISTANCE_OUT(18u).dat"
[Output] LAST_FAS_LLM: file "LAST_FAS_LLM(8u).dat"
[Output] LAST_FAS_LOGICAL_LANE: file "LAST_FAS_LOGICAL_LANE(5u).dat"
[Output] LAST_FAS_PHYSICAL_LANE: file "LAST_FAS_PHYSICAL_LANE(5u).dat"
[Output] LOGICAL_LANES_CHANNELS: file "LOGICAL_LANES_CHANNELS_TO_LOGICAL_LANES_OUT(5u).dat"
[Output] LOGICAL_LANES_DETECTION_DEGREE: file "LOGICAL_LANES_DETECTION_DEGREE(3u).dat"
[Output] OTL4_10_LOCK: file "OTL4_10_LOCK(1u).dat"
[Output] OTL4_10_OUTPUT_BUFFER_OVERFLOW_ERROR: file "OTL4_10_OUTPUT_BUFFER_OVERFLOW_ERROR(1u).dat"
[Output] OTL_LOFLANE: file "OTL_LOFLANE(1u).dat"
[Output] OTL_LOL: file "OTL_LOL(1u).dat"
[Output] OTL_LOR: file "OTL_LOR(1u).dat"
[Output] OTL_OOFLANE: file "OTL_OOFLANE(1u).dat"
[Output] OTL_OOR: file "OTL_OOR(1u).dat"
[Output] OTU4_OUTPUT: file "OTU4_OUTPUT(1u).dat"
[Output] OTU_LOF: file "OTU_LOF(1u).dat"
[Output] OTU_LOM: file "OTU_LOM(1u).dat"
[Output] OTU_OOF: file "OTU_OOF(1u).dat"
[Output] OTU_OOM: file "OTU_OOM(1u).dat"
[Output] Fields without files: SEARCH_LANE_CHANNEL
[Output] Total fields: 23, Fields with file: 22
```
